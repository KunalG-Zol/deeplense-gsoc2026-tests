from pydantic import BaseModel, Field
from typing import Literal, Annotated, Union

# Basic Parameters required for initializing the Deeplense object
class BaseSimParams(BaseModel):
    num_images: int = Field(1, ge=1, description="Number of images to generate")
    z_lens: float = Field(0.5, gt=0.0, description="Redshift of the primary lens galaxy")
    num_pix: int = Field(150, ge=32, description="Resolution of the output image in pixels")
    halo_mass: float = Field(1e12, gt=0.0, description="Mass of the main dark matter halo in solar masses")
    z_halo: float = Field(0.5, gt=0.0, description="Redshift of the dark matter halo")
    z_gal: float = Field(1.0, gt=0.0, description="Redshift of the background source galaxy")
    h0: float = Field(70.0, gt=0.0, description="Hubble constant (H0) in km/s/Mpc")
    ob0: float = Field(0.05, gt=0.0, le=1.0, description="Baryonic matter density parameter")
    om0: float = Field(0.3, gt=0.0, le=1.0, description="Total matter density parameter")

# Schemas for the 3 classes (no substructure, axion and cdm)
class NoSub(BaseModel):
    sim_class: Literal["no_sub"] = Field("no_sub", description="Smooth lens model without dark matter substructure")

class CDM(BaseModel):
    sim_class: Literal["cdm"] = Field("cdm", description="Cold Dark Matter model with subhalo populations")
    instrument: str = Field("Euclid", description="Telescope instrument profile to simulate")
class Axion(BaseModel):
    sim_class: Literal["axion"] = Field("axion", description="Fuzzy Dark Matter model with wave interference")
    axion_mass_min: float = Field(-24.0, description="Base-10 logarithm of the minimum axion mass in eV")
    axion_mass_max: float = Field(-22.0, description="Base-10 logarithm of the maximum axion mass in eV")
    vortex_mass: float = Field(3e10, gt=0.0, description="Mass of the vortex perturbation in solar masses")

PhysicsUnion = Annotated[
    Union[NoSub, CDM, Axion],
    Field(discriminator="sim_class", description="The specific dark matter physics configuration to apply")
]

Here are the complete schemas for the Models.

I removed the instrument field from the CDM class and moved it into Model2Config and Model3Config. In observational astronomy, an instrument like Euclid or HST dictates the Point Spread Function (PSF) and noise properties of the entire image, not just the dark matter clumps. Placing it at the Model level ensures the agent applies the telescope effects to smooth lenses and axion vortices as well.

Python
from pydantic import BaseModel, Field
from typing import Literal, Annotated, Union

class BaseSimParams(BaseModel):
    num_images: int = Field(1, ge=1, description="Number of images to generate")
    z_lens: float = Field(0.5, gt=0.0, description="Redshift of the primary lens galaxy")
    num_pix: int = Field(150, ge=32, description="Resolution of the output image in pixels")
    halo_mass: float = Field(1e12, gt=0.0, description="Mass of the main dark matter halo in solar masses")
    z_halo: float = Field(0.5, gt=0.0, description="Redshift of the dark matter halo")
    z_gal: float = Field(1.0, gt=0.0, description="Redshift of the background source galaxy")
    h0: float = Field(70.0, gt=0.0, description="Hubble constant (H0) in km/s/Mpc")
    ob0: float = Field(0.05, gt=0.0, le=1.0, description="Baryonic matter density parameter")
    om0: float = Field(0.3, gt=0.0, le=1.0, description="Total matter density parameter")

class NoSub(BaseModel):
    sim_class: Literal["no_sub"] = Field("no_sub", description="Smooth lens model without dark matter substructure")

class CDM(BaseModel):
    sim_class: Literal["cdm"] = Field("cdm", description="Cold Dark Matter model with subhalo populations")

class Axion(BaseModel):
    sim_class: Literal["axion"] = Field("axion", description="Fuzzy Dark Matter model with wave interference")
    axion_mass_min: float = Field(-24.0, description="Base-10 logarithm of the minimum axion mass in eV")
    axion_mass_max: float = Field(-22.0, description="Base-10 logarithm of the maximum axion mass in eV")
    vortex_mass: float = Field(3e10, gt=0.0, description="Mass of the vortex perturbation in solar masses")

PhysicsUnion = Annotated[
    Union[NoSub, CDM, Axion],
    Field(discriminator="sim_class", description="The specific dark matter physics configuration to apply")
]

# Schemas differentiating the models
class Model1Config(BaseSimParams):
    model_choice: Literal["Model_I"] = Field("Model_I", description="Model I configuration")
    physics: PhysicsUnion

class Model2Config(BaseSimParams):
    model_choice: Literal["Model_II"] = Field("Model_II", description="Model II configuration")
    instrument: Literal["Euclid", "HST"] = Field("Euclid", description="Telescope instrument profile to simulate")
    physics: PhysicsUnion

class Model3Config(BaseSimParams):
    model_choice: Literal["Model_III"] = Field("Model_III", description="Model III configuration")
    instrument: Literal["Euclid", "HST"] = Field("HST", description="Telescope instrument profile to simulate")
    physics: PhysicsUnion

DeepLenseRequest = Annotated[
    Union[Model1Config, Model2Config, Model3Config],
    Field(discriminator="model_choice", description="The top-level model routing configuration")
]