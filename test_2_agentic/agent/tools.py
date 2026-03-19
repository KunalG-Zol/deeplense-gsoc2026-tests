import random
import numpy as np
from pathlib import Path
from deeplense.lens import DeepLens


def _create_save_dir(model_label: str, sim_class: str) -> Path:
    save_dir = Path(f"./outputs/{model_label}/{sim_class}")
    save_dir.mkdir(parents=True, exist_ok=True)
    return save_dir

def _get_axion_masses(config):
    if config.physics.sim_class == "axion":
        return 10 ** np.random.uniform(
            config.physics.axion_mass_min,
            config.physics.axion_mass_max,
            config.num_images
        )
    return None

def _initialize_lens(config, axion_mass):
    lens = DeepLens(
        axion_mass=axion_mass,
        H0=config.H0,
        Om0=config.Om0,
        Ob0=config.Ob0,
        z_halo=config.z_halo,
        z_gal=config.z_gal
    )
    lens.make_single_halo(config.halo_mass)
    return lens

def _apply_substructure(lens, config):
    if config.physics.sim_class == 'axion':
        lens.make_vortex(vort_mass=config.physics.vortex_mass)
    elif config.physics.sim_class == 'no_sub':
        lens.make_no_sub()
    else:
        lens.make_old_cdm()
    return lens


def _run_sim(lens, model_label, config):
    if model_label == 'Model_I':
        lens.make_source_light()
        lens.simple_sim()
    else:
        lens.set_instrument(config.instrument)
        lens.make_source_light_mag()
        lens.simple_sim_2()
    return lens


def _save_simulation(lens, config, axion_mass, save_dir):
    if config.physics.sim_class == 'axion':
        File = np.array([lens.image_real, axion_mass], dtype=object)
    else:
        File = lens.image_real

    file_name = f"{config.physics.sim_class}_sim_{random.getrandbits(128)}.npy"
    np.save(save_dir / file_name, File)

async def execute_simulation(config, model_label: str):
    save_dir = _create_save_dir(model_label, config.physics.sim_class)
    axion_masses = _get_axion_masses(config)
    for i in range(config.num_images):
        axion_mass = axion_masses[i] if axion_masses is not None and axion_masses.size > 0 else None

        lens = _initialize_lens(config, axion_mass)
        lens = _apply_substructure(lens, config)
        lens = _run_sim(lens, model_label, config)

        _save_simulation(lens, config, axion_mass, save_dir)

    return 'Simulation ran succesfully'


async def run_model_1_sim(config):
    return await execute_simulation(config, "Model_I")


async def run_model_2_sim(config):
    return await execute_simulation(config, "Model_II")


async def run_model_3_sim(config):
    return await execute_simulation(config, "Model_III")
