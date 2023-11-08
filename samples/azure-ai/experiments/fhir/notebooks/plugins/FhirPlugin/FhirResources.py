from fhirclient import client
from fhirclient.models.condition import Condition
from fhirclient.models.medication import Medication
from fhirclient.models.medicationrequest import MedicationRequest
from fhirclient.models.patient import Patient
from fhirclient.models.observation import Observation
from semantic_kernel.skill_definition import sk_function

settings = {
  'app_id': 'fhir_lookup',
  'api_base': 'http://hapi.fhir.org/baseR4'
}
fhir_client = client.FHIRClient(settings=settings)


class FhirResources:

  @sk_function(
    description="Retrieves conditions for the given patient",
    name="Conditions",
    input_description="The patient identifier for whom conditions will be retrieved"
  )
  def get_conditions(self, patient_id: str) -> str:
    return "to be implemented"
  
  @sk_function(
    description="Retrieves observations for the given patient",
    name="Observations",
    input_description="The patient identifier for whom observations will be retrieved"
  )
  def get_observations(self, patient_id: str) -> str:
    return "to be implemented"

  @sk_function(
    description="Retrieves questionnaire responses for the given patient",
    name="QuestionnaireResponses",
    input_description="The patient identifier for whom questionnaire responses will be retrieved"
  )
  def get_questionnaire_responses(self, patient_id: str) -> str:
    return "to be implemented"

  @sk_function(
    description="Retrieves medication requests for the given patient",
    name="MedicationRequests",
    input_description="The patient identifier for whom medication requests will be retrieved"
  )
  def get_medication_requests(self, patient_id: str) -> str:
    return "to be implemented"

  @sk_function(
    description="Retrieves precedures for the given patient",
    name="Procedures",
    input_description="The patient identifier for whom procedures will be retrieved"
  )
  def get_procedures(self, patient_id: str) -> str:
    return "to be implemented"
