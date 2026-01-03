import logging
import numpy as np
import pickle

from dynamicforaging_mle_model import (
    DynamicForagingModelFittingOutputs,
)
from s3_nwb_util import discover_nwb_files_s3
import aind_dynamic_foraging_data_utils.nwb_utils as nu
from aind_dynamic_foraging_models.generative_model import ForagerCollection

logger = logging.getLogger(__name__)
RESULTS_FOLDER = "/results"

def mle_wrapper(s3_location, analysis_args) -> DynamicForagingModelFittingOutputs:
    """
    Wrapper for the Dynamic Foraging MLE analysis.

    Parameters
    ----------
    s3_location: str
        The S3 location of the NWB file to process
    analysis_args: dict
        The analysis arguments extracted from the analysis dispatch model

    Returns
    -------
    output_parameters: DynamicForagingModelFittingOutputs
        The output parameters of the analysis
    """

    # -- Locate NWB files --
    nwb_uri = discover_nwb_files_s3(s3_location)
    if not nwb_uri:
        logger.warning("No NWB file found, skipping processing.")
        return

    # -- Load NWB and extract choice and reward history --
    logger.info(f"Found NWB file to process: {nwb_uri}")
    logger.info(f"Processing {nwb_uri}")

    df_trial = nu.create_df_trials(nwb_uri, adjust_time=False, verbose=False, forced_sanity_check=False)
    choice_history = df_trial.animal_response.map({0: 0, 1: 1, 2: np.nan}).values
    reward_history = df_trial.rewarded_historyL | df_trial.rewarded_historyR
    
    # Additional metadata for result-access to directly query
    # (ideally they should be added to the upper layer metadata)
    nwb = nu.load_nwb_from_filename(nwb_uri)
    subject_id = nwb.subject.subject_id
    session_date = nwb.session_start_time.strftime("%Y-%m-%d")
    nwb_name = nwb_uri.split("/")[-1]

    # Remove ignored trials
    ignored = np.isnan(choice_history)
    choice_history = choice_history[~ignored]
    reward_history = reward_history[~ignored].to_numpy()

    # Skip if len(valid trials) < 50
    if len(choice_history) < 50:
        return DynamicForagingModelFittingOutputs(
            subject_id=subject_id, 
            session_date=session_date,
            nwb_name=nwb_name,
            fitting_results={}, 
            additional_info="skipped. valid trials < 50"
        )

    # -- Initialize model and fit --
    forager = ForagerCollection().get_forager(
        agent_class_name=analysis_args["agent_class"],
        agent_kwargs=analysis_args["agent_kwargs"],
    )
    forager.fit(
        choice_history,
        reward_history,
        **analysis_args["fit_kwargs"],
        )

    # -- Saving results --
    # Database record
    fitting_results = forager.get_fitting_result_dict()

    # Save figures
    fig_fitting, _ = forager.plot_fitted_session(if_plot_latent=True)
    fig_fitting.savefig(f"{RESULTS_FOLDER}/fitted_session.png", dpi=500)
    logger.info(f"Saved fitting figure to {RESULTS_FOLDER}/fitted_session.png")
    
    # Save the forager object
    # Have to flatten pydantic models in forager for pickle to work
    forager.ParamModel = forager.ParamModel.model_json_schema()
    forager.ParamFitBoundModel = forager.ParamFitBoundModel.schema_json()
    forager.params = forager.params.model_dump()
    with open(f"{RESULTS_FOLDER}/forager.pkl", "wb") as f:
        pickle.dump(forager, f)
    logger.info(f"Saved forager object to {RESULTS_FOLDER}/forager.pkl")    

    return DynamicForagingModelFittingOutputs(
        subject_id=subject_id, 
        session_date=session_date,
        nwb_name=nwb_name,
        fitting_results=fitting_results,
        additional_info="success",
    )
