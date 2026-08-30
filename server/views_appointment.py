from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.db.models import Q

from server.forms import AppointmentForm
from server.models import Account, Appointment, Action

from server import views
from server import appointment
from server import logger
from server import message


def list_view(request):

    # Authentication check
    authentication_result = views.authentication_check(
        request,
        [Account.ACCOUNT_PATIENT, Account.ACCOUNT_DOCTOR]
    )

    if authentication_result is not None:
        return authentication_result

    # Get template data from session
    template_data = views.parse_session(request)

    # Parse appointment cancelling
    appointment.parse_appointment_cancel(request, template_data)

    if request.user.account.role == Account.ACCOUNT_DOCTOR:
        template_data['query'] = Appointment.objects.filter(
            doctor=request.user.account
        )

    elif request.user.account.role == Account.ACCOUNT_PATIENT:
        template_data['query'] = Appointment.objects.filter(
            patient=request.user.account
        )

    else:
        template_data['query'] = Appointment.objects.all()

    return render(
        request,
        'virtualclinic/appointment/list.html',
        template_data
    )


def calendar_view(request):

    # Authentication check
    authentication_result = views.authentication_check(
        request,
        [Account.ACCOUNT_PATIENT, Account.ACCOUNT_DOCTOR]
    )

    if authentication_result is not None:
        return authentication_result

    # Get template data from session
    template_data = views.parse_session(request)

    appointment.parse_appointment_cancel(request, template_data)

    template_data['events'] = appointment.parse_appointments(request)

    return render(
        request,
        'virtualclinic/appointment/calendar.html',
        template_data
    )


def update_view(request):

    # Authentication check
    authentication_result = views.authentication_check(
        request,
        None,
        ['pk']
    )

    if authentication_result is not None:
        return authentication_result

    pk = request.GET['pk']

    try:
        appointment_obj = Appointment.objects.get(pk=pk)
    except Appointment.DoesNotExist:
        request.session['alert_danger'] = (
            "The requested appointment does not exist."
        )
        return HttpResponseRedirect('/error/denied/')

    # Get template data
    template_data = views.parse_session(
        request,
        {
            'form_button': "Update Appointment",
            'form_action': "?pk=" + pk,
            'appointment': appointment_obj
        }
    )

    request.POST._mutable = True

    if request.user.account.role == Account.ACCOUNT_PATIENT:
        request.POST['patient'] = request.user.account.pk

    elif request.user.account.role == Account.ACCOUNT_DOCTOR:
        request.POST['doctor'] = request.user.account.pk

    if request.method == 'POST':

        form = AppointmentForm(request.POST)

        if form.is_valid():

            form.assign(appointment_obj)

            conflict = Appointment.objects.filter(
                ~Q(pk=appointment_obj.pk),
                Q(status="Active"),
                Q(
                    doctor=appointment_obj.doctor
                ) | Q(
                    patient=appointment_obj.patient
                ),
                Q(
                    startTime__range=(
                        appointment_obj.startTime,
                        appointment_obj.endTime
                    )
                ) | Q(
                    endTime__range=(
                        appointment_obj.startTime,
                        appointment_obj.endTime
                    )
                )
            ).count()

            if conflict:

                form.mark_error(
                    'startTime',
                    'This time conflicts with another appointment.'
                )

                form.mark_error(
                    'endTime',
                    'This time conflicts with another appointment.'
                )

            else:

                appointment_obj.save()

                logger.log(
                    Action.ACTION_APPOINTMENT,
                    'Appointment Updated',
                    request.user.account
                )

                template_data['alert_success'] = (
                    "The appointment has been updated!"
                )

                if request.user.account.role == Account.ACCOUNT_PATIENT:
                    message.send_appointment_update(
                        request,
                        appointment_obj,
                        appointment_obj.doctor
                    )

                elif request.user.account.role == Account.ACCOUNT_DOCTOR:
                    message.send_appointment_update(
                        request,
                        appointment_obj,
                        appointment_obj.patient
                    )

                else:
                    message.send_appointment_update(
                        request,
                        appointment_obj,
                        appointment_obj.patient
                    )

                    message.send_appointment_update(
                        request,
                        appointment_obj,
                        appointment_obj.doctor
                    )

    else:
        form = AppointmentForm(
            appointment_obj.get_populated_fields()
        )

    if request.user.account.role == Account.ACCOUNT_PATIENT:
        form.disable_field('patient')

    elif request.user.account.role == Account.ACCOUNT_DOCTOR:
        form.disable_field('doctor')

    template_data['form'] = form

    return render(
        request,
        'virtualclinic/appointment/update.html',
        template_data
    )


def create_view(request):

    # Authentication check
    authentication_result = views.authentication_check(
        request,
        [Account.ACCOUNT_PATIENT, Account.ACCOUNT_DOCTOR]
    )

    if authentication_result is not None:
        return authentication_result

    template_data = views.parse_session(
        request,
        {'form_button': "Create"}
    )

    default = {}

    if request.user.account.role == Account.ACCOUNT_PATIENT:

        default['patient'] = request.user.account.pk

        if (
            'doctor' not in request.POST
            and request.user.account.profile.primaryCareDoctor is not None
        ):
            default['doctor'] = (
                request.user.account.profile.primaryCareDoctor.pk
            )

    elif request.user.account.role == Account.ACCOUNT_DOCTOR:

        default['doctor'] = request.user.account.pk

    if (
        'hospital' not in request.POST
        and request.user.account.profile.prefHospital is not None
    ):
        default['hospital'] = (
            request.user.account.profile.prefHospital.pk
        )

    request.POST._mutable = True
    request.POST.update(default)

    form = AppointmentForm(request.POST)

    if request.method == 'POST':

        if form.is_valid():

            appointment_obj = form.generate()

            conflict = Appointment.objects.filter(
                Q(status="Active"),
                Q(
                    doctor=appointment_obj.doctor
                ) | Q(
                    patient=appointment_obj.patient
                ),
                Q(
                    startTime__range=(
                        appointment_obj.startTime,
                        appointment_obj.endTime
                    )
                ) | Q(
                    endTime__range=(
                        appointment_obj.startTime,
                        appointment_obj.endTime
                    )
                )
            ).count()

            if conflict:

                form.mark_error(
                    'startTime',
                    'This time conflicts with another appointment'
                )

                form.mark_error(
                    'endTime',
                    'This time conflicts with another appointment'
                )

            else:

                appointment_obj.save()

                logger.log(
                    Action.ACTION_APPOINTMENT,
                    'Appointment created',
                    request.user.account
                )

                form = AppointmentForm(default)
                form._errors = {}

                request.session['alert_success'] = (
                    "Successfully created your appointment!"
                )

                if request.user.account.role == Account.ACCOUNT_DOCTOR:

                    message.send_appointment_create(
                        request,
                        appointment_obj,
                        appointment_obj.patient
                    )

                elif request.user.account.role == Account.ACCOUNT_PATIENT:

                    message.send_appointment_create(
                        request,
                        appointment_obj,
                        appointment_obj.doctor
                    )

                else:

                    message.send_appointment_create(
                        request,
                        appointment_obj,
                        appointment_obj.patient
                    )

                    message.send_appointment_create(
                        request,
                        appointment_obj,
                        appointment_obj.doctor
                    )

                return HttpResponseRedirect(
                    '/ai/?appointment_id={}'.format(
                        appointment_obj.pk
                    )
                )

    else:
        form._errors = {}

    if request.user.account.role == Account.ACCOUNT_PATIENT:
        form.disable_field('patient')

    elif request.user.account.role == Account.ACCOUNT_DOCTOR:
        form.disable_field('doctor')

    template_data['form'] = form

    return render(
        request,
        'virtualclinic/appointment/create.html',
        template_data
    )