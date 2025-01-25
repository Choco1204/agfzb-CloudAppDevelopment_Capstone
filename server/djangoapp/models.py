from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

# <HINT> Create a Car Make model `class CarMake(models.Model)`:
# - Name
# - Description
# - Any other fields you would like to include in car make model
# - __str__ method to print a car make object


class CarMake(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="The name of the car manufacturer (e.g., Toyota)",
    )
    description = models.TextField(help_text="Detailed description of the car make")
    country_of_origin = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Headquarters country (e.g., Japan)",
    )
    founded_year = models.PositiveIntegerField(
        blank=True, null=True, help_text="Year the company was founded"
    )
    website = models.URLField(blank=True, help_text="Official website URL")
    logo = models.ImageField(
        upload_to="make_logos/", blank=True, null=True, help_text="Company logo image"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Car Manufacturer"
        verbose_name_plural = "Car Manufacturers"
        ordering = ["name"]


# <HINT> Create a Car Model model `class CarModel(models.Model):`:
# - Many-To-One relationship to Car Make model (One Car Make has many Car Models, using ForeignKey field)
# - Name
# - Dealer id, used to refer a dealer created in cloudant database
# - Type (CharField with a choices argument to provide limited choices such as Sedan, SUV, WAGON, etc.)
# - Year (DateField)
# - Any other fields you would like to include in car model
# - __str__ method to print a car make object
class CarModel(models.Model):
    # Relationship to CarMake
    make = models.ForeignKey(
        "CarMake",
        on_delete=models.CASCADE,
        related_name="models",
        help_text="Manufacturer of the vehicle",
    )

    # Cloudant reference
    dealer_id = models.IntegerField(help_text="ID of dealer in Cloudant database")

    # Model information
    name = models.CharField(max_length=100, help_text="Model name (e.g., Camry)")

    # Type choices
    TYPE_CHOICES = [
        ("Sedan", "Sedan"),
        ("SUV", "SUV"),
        ("Wagon", "Wagon"),
        ("Truck", "Truck"),
        ("Coupe", "Coupe"),
    ]
    type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, help_text="Body style of the vehicle"
    )

    # Year field with validation
    year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(timezone.now().year + 1),  # Allow future models
        ],
        help_text="Production year",
    )

    # Additional fields
    engine_options = models.CharField(
        max_length=200, blank=True, help_text="Available engine configurations"
    )
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Starting MSRP",
    )
    safety_rating = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="NHTSA safety rating (0-5)",
    )

    def __str__(self):
        return f"{self.make.name} {self.name} ({self.year}) - {self.type}"

    class Meta:
        verbose_name = "Vehicle Model"
        verbose_name_plural = "Vehicle Models"
        ordering = ["-year", "make__name", "name"]
        unique_together = ["make", "name", "year"]


# <HINT> Create a plain Python class `CarDealer` to hold dealer data


# <HINT> Create a plain Python class `DealerReview` to hold review data
