from django.core.management.base import BaseCommand
from search.models import Patients

class Command(BaseCommand):
    help = 'Calculates and stores average respiratory cycle durations for each patient'

    def handle(self, *args, **options):
        results = Patients.calculate_average_cycle_durations()
        print(results)
        for result in results:
            patient_id = result['_id']  # Adjust depending on your grouping key
            average_duration = result['average_cycle_duration']
            print(patient_id)
            print(average_duration)
            patient = Patients.objects.get(pk=patient_id)
            patient.average_cycle_duration = average_duration
            patient.save()
            self.stdout.write(self.style.SUCCESS(f'Updated patient {patient_id} with average cycle duration {average_duration}.'))
