
import logging

from dynamicforaging_mle_model import (
    DynamicForagingModelFittingOutputs,
)
from s3_nwb_util import discover_nwb_files_s3
import aind_dynamic_foraging_data_utils.nwb_utils as nu
from aind_dynamic_foraging_models.generative_model import ForagerCollection

logger = logging.getLogger(__name__)

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
    
    df_trial = nu.create_df_trials(nwb_uri, adjust_time=False, verbose=False)
    choice_history = df_trial.animal_response.map({0: 0, 1: 1, 2: np.nan}).values
    reward_history = df_trial.rewarded_historyL | df_trial.rewarded_historyR
    
    # Remove ignored trials
    ignored = np.isnan(choice_history)
    choice_history = choice_history[~ignored]
    reward_history = reward_history[~ignored].to_numpy()
    
    # Skip if len(valid trials) < 50
    if len(choice_history) < 50:
        return {
            "status": "skipped. valid trials < 50",
            "upload_figs_s3": {},
            "upload_pkls_s3": {},
            "upload_record_docDB": {},
        }

    # Initialize model and fit
    forager = ForagerCollection().get_forager(
        agent_class_name=analysis_args["agent_class"],
        agent_kwargs=analysis_args["agent_kwargs"],
        )
    forager.fit(
        choice_history,
        reward_history,
        **analysis_args["fit_kwargs"],
        )
        
    return DynamicForagingModelFittingOutputs(
        isi_violations=["example_violation_1", "example_violation_2"],
        additional_info=(
            "This is an example of additional information about the analysis."
        ),
    )