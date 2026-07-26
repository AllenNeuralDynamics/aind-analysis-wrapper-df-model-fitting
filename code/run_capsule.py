from analysis_pipeline_utils.analysis_dispatch_model import \
    AnalysisDispatchModel
from analysis_pipeline_utils.utils_analysis_wrapper import (
    run_analysis_jobs)
from dotenv import load_dotenv

from dynamicforaging_mle_model import (
    DynamicForagingModelFittingOutputs,
    DynamicForagingModelFittingSpecification,
)
from dynamicforaging_mle_wrapper import mle_wrapper

# TODO: use pydantic settings instead
load_dotenv("settings.env")

AnalysisInputModel = DynamicForagingModelFittingSpecification
AnalysisOutputModel = DynamicForagingModelFittingOutputs



def run_analysis(
    analysis_dispatch_inputs: AnalysisDispatchModel,
    analysis_parameters: AnalysisInputModel,
) -> dict:
    """
    Run MLE model fitting for one dispatched job.

    Parameters
    ----------
    analysis_dispatch_inputs: AnalysisDispatchModel
        The input model with input data from the dispatcher

    analysis_parameters: AnalysisInputModel
        The validated analysis parameters for this job

    Returns
    -------
    dict
        Output parameters, validated against AnalysisOutputModel by
        run_analysis_jobs. Large artifacts (figures, pickled forager,
        full fitting results) are written to /results by mle_wrapper.
    """
    return mle_wrapper(
        s3_location=analysis_dispatch_inputs.s3_location,
        analysis_args=analysis_parameters.model_dump(),
    )


if __name__ == "__main__":
    run_analysis_jobs(
        analysis_input_model=AnalysisInputModel,
        analysis_output_model=AnalysisOutputModel,
        run_function=run_analysis
    )
