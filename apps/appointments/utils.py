import datetime
from .models import Appointment
from apps.staff.models import WorkSchedule


def get_available_slots(staff, service, date, current_customer=None):
    """
    زمان‌های خالی یک کارکن برای یک خدمت در یک تاریخ
    current_customer: اگه مشتری مشخص باشه، نوبت‌های همون مشتری تداخل حساب نمیشه
    """
    python_to_iranian = {
        0: 2, 1: 3, 2: 4, 3: 5, 4: 6, 5: 0, 6: 1,
    }
    iranian_day = python_to_iranian[date.weekday()]

    try:
        schedule = WorkSchedule.objects.get(
            staff=staff,
            day_of_week=iranian_day,
            is_available=True
        )
    except WorkSchedule.DoesNotExist:
        return []

    # نوبت‌های رزرو شده در اون روز
    booked_query = Appointment.objects.filter(
        staff=staff,
        date=date,
        status__in=['pending', 'confirmed']
    )

    # اگه مشتری مشخص شده، نوبت‌های همون مشتری رو از چک تداخل خارج کن
    if current_customer:
        booked_query = booked_query.exclude(customer=current_customer)

    booked_slots = list(booked_query.values('start_time', 'end_time'))
    booked_list = [(a['start_time'], a['end_time']) for a in booked_slots]

    duration = service.duration
    slots = []

    current = datetime.datetime.combine(date, schedule.start_time)
    end_of_day = datetime.datetime.combine(date, schedule.end_time)

    while current + datetime.timedelta(minutes=duration) <= end_of_day:
        slot_start = current.time()
        slot_end = (current + datetime.timedelta(minutes=duration)).time()

        # چک تداخل با نوبت‌های مشتریان دیگه
        is_available = True
        for booked_start, booked_end in booked_list:
            if not (slot_end <= booked_start or slot_start >= booked_end):
                is_available = False
                break

        # فقط زمان‌های آینده
        now = datetime.datetime.now()
        slot_datetime = datetime.datetime.combine(date, slot_start)
        if slot_datetime > now and is_available:
            slots.append({
                'start': slot_start.strftime('%H:%M'),
                'end': slot_end.strftime('%H:%M'),
                'value': slot_start.strftime('%H:%M'),
            })

        current += datetime.timedelta(minutes=duration)

    return slots