import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone

from .timestamped import TimestampedModel


class CallTime:
    WEEK_DAY = "WEEK_DAY"
    WEEK_EVENING = "WEEK_EVENING"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class ReferrerType:
    LEGAL_CENTRE = "LEGAL_CENTRE"
    CHARITY = "CHARITY"
    SEARCH = "SEARCH"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    WORD_OF_MOUTH = "WORD_OF_MOUTH"
    ONLINE_AD = "ONLINE_AD"
    HOUSING_SERVICE = "HOUSING_SERVICE"
    RADIO = "RADIO"
    BILLBOARD = "BILLBOARD"
    POSTER = "POSTER"


class GenderType:
    MALE = "male"
    FEMALE = "female"
    GENDERQUEER = "genderqueer"
    OMITTED = "omitted"
    OTHER = "other"


class EmploymentType:
    WORKING_PART_TIME = "WORKING_PART_TIME"
    WORKING_FULL_TIME = "WORKING_FULL_TIME"
    APPRENTICE = "APPRENTICE"
    LOOKING_FOR_WORK = "LOOKING_FOR_WORK"
    INCOME_REDUCED_COVID = "INCOME_REDUCED_COVID"
    RETIRED = "RETIRED"


class CircumstanceType:
    CENTRELINK = "CENTRELINK"
    MENTAL_ILLNESS_OR_DISABILITY = "MENTAL_ILLNESS_OR_DISABILITY"
    PUBLIC_HOUSING = "PUBLIC_HOUSING"
    FAMILY_VIOLENCE = "FAMILY_VIOLENCE"
    HEALTH_CONDITION = "HEALTH_CONDITION"
    REFUGEE = "REFUGEE"


class LegalAccessType:
    SUBSTANCE_ABUSE = "SUBSTANCE_ABUSE"
    CARING = "CARING"
    DISABILITY = "DISABILITY"
    OTHER = "OTHER"


class RentalType:
    SOLO = "SOLO"
    FLATMATES = "FLATMATES"
    PARTNER = "PARTNER"
    FAMILY = "FAMILY"
    OTHER = "OTHER"


class Client(TimestampedModel):
    """
    A person that we are helping.
    """

    GENDER_CHOICES = (
        (GenderType.MALE, "Male"),
        (GenderType.FEMALE, "Female"),
        (GenderType.GENDERQUEER, "Genderqueer"),
        (GenderType.OMITTED, "Omitted"),
        (GenderType.OTHER, "Other"),
    )
    EMPLOYMENT_CHOICES = (
        (EmploymentType.WORKING_PART_TIME, "Working part time"),
        (EmploymentType.WORKING_FULL_TIME, "Working full time"),
        (EmploymentType.APPRENTICE, "Apprentice"),
        (EmploymentType.LOOKING_FOR_WORK, "Looking for work"),
        (EmploymentType.INCOME_REDUCED_COVID, "Income reduced due to COVID-19"),
        (EmploymentType.RETIRED, "Retired"),
    )
    CIRCUMSTANCE_CHOICES = (
        (CircumstanceType.CENTRELINK, "Centrelink"),
        (CircumstanceType.MENTAL_ILLNESS_OR_DISABILITY, "Mental illness or disability"),
        (CircumstanceType.PUBLIC_HOUSING, "Public housing"),
        (CircumstanceType.FAMILY_VIOLENCE, "Risk of family violence"),
        (CircumstanceType.HEALTH_CONDITION, "Health condition"),
        (CircumstanceType.REFUGEE, "Refugee"),
    )
    LEGAL_ACCESS_CHOICES = (
        (LegalAccessType.SUBSTANCE_ABUSE, "Substance abuse issues"),
        (LegalAccessType.CARING, "Caring for another"),
        (LegalAccessType.DISABILITY, "Disability"),
        (LegalAccessType.OTHER, "Other"),
    )
    RENTAL_CHOICES = (
        (RentalType.SOLO, "Renting solo"),
        (RentalType.FLATMATES, "Renting with flatmates"),
        (RentalType.PARTNER, "Renting with a partner"),
        (RentalType.FAMILY, "Renting with family"),
        (RentalType.OTHER, "Other"),
    )
    CALL_TIME_CHOICES = (
        (CallTime.WEEK_DAY, "Week day"),
        (CallTime.WEEK_EVENING, "Week evening"),
        (CallTime.SATURDAY, "Saturday"),
        (CallTime.SUNDAY, "Sunday"),
    )

    REFERRER_TYPE_CHOICES = (
        (ReferrerType.LEGAL_CENTRE, "Legal centre"),
        (ReferrerType.CHARITY, "Charity"),
        (ReferrerType.SEARCH, "Search"),
        (ReferrerType.SOCIAL_MEDIA, "Social media"),
        (ReferrerType.WORD_OF_MOUTH, "Word of mouth"),
        (ReferrerType.ONLINE_AD, "Online ad"),
        (ReferrerType.HOUSING_SERVICE, "Housing service"),
        (ReferrerType.RADIO, "Radio"),
        (ReferrerType.BILLBOARD, "Billboard"),
        (ReferrerType.POSTER, "Poster"),
    )

    # Identifying info
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    # Contact details
    email = models.EmailField(max_length=150)
    date_of_birth = models.DateTimeField(null=True, blank=True)
    phone_number = models.CharField(max_length=32, blank=True, default="")
    call_times = ArrayField(
        models.CharField(max_length=32, choices=CALL_TIME_CHOICES),
        default=list,
        blank=True,
    )

    # Demographic info for impact analysis.
    employment_status = ArrayField(
        models.CharField(max_length=32, choices=EMPLOYMENT_CHOICES),
        default=list,
        blank=True,
    )

    special_circumstances = ArrayField(
        models.CharField(max_length=32, choices=CIRCUMSTANCE_CHOICES),
        default=list,
        blank=True,
    )
    weekly_income = models.IntegerField(null=True, blank=True)
    weekly_rent = models.IntegerField(null=True, blank=True)
    gender = models.CharField(
        max_length=64, null=True, choices=GENDER_CHOICES, blank=True
    )
    primary_language_non_english = models.BooleanField(default=False)
    primary_language = models.CharField(max_length=32, blank=True, default="")
    is_aboriginal_or_torres_strait_islander = models.BooleanField(default=False)
    rental_circumstances = models.CharField(
        max_length=32, choices=RENTAL_CHOICES, blank=True, default=""
    )
    is_multi_income_household = models.BooleanField(null=True)
    number_of_dependents = models.IntegerField(null=True)
    legal_access_difficulties = ArrayField(
        models.CharField(max_length=32, choices=LEGAL_ACCESS_CHOICES),
        default=list,
        blank=True,
    )

    # Referrer info: how did the client find us?
    referrer_type = models.CharField(
        max_length=64, choices=REFERRER_TYPE_CHOICES, blank=True, default=""
    )
    # Specific referrer name.
    referrer = models.CharField(max_length=64, blank=True, default="")

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def get_age(self) -> int:
        return int((timezone.now() - self.date_of_birth).days / 365.25)

    def __str__(self) -> str:
        name = self.get_full_name()
        return f"{name} ({self.id})"
