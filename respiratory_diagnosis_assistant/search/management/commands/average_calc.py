from django.core.management.base import BaseCommand
from search.models import Patients

class Command(BaseCommand):
    help = 'Calculates and stores average respiratory cycle durations for each patient'

    def handle(self, *args, **options):
        results = Patients.calculate_average_cycle_durations()
        for result in results:
            patient_id = result['patient_id']
            average_duration = result['average_cycle_duration']
            patient = Patients.objects.get(patient_id=patient_id)
            patient.average_cycle_duration = average_duration
            patient.save()
