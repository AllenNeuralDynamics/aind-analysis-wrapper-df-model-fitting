import json
import logging
import os
from typing import Iterable, List, Optional, Sequence, Union

from analysis_pipeline_utils.analysis_dispatch_model import \
    AnalysisDispatchModel
from analysis_pipeline_utils.metadata import (construct_processing_record,
                                              docdb_record_exists,
                                              write_results_and_metadata)
from analysis_pipeline_utils.utils_analysis_wrapper import (
    get_analysis_model_parameters, make_cli_model)

from df_mle_model import (
    DynamicForagingModelFittingOutputs,
    DynamicForagingModelFittingSpecification,
)
from s3_nwb_util import discover_nwb_files_s3

ANALYSIS_BUCKET = os.getenv("ANALYSIS_BUCKET")
logger = logging.getLogger(__name__)


def run_analysis(
    analysis_dispatch_inputs: AnalysisDispatchModel,
    dry_run: bool = True,
    **parameters,
) -> None:
    """
    Runs the analysis

    Parameters
    ----------
    analysis_dispatch_inputs: AnalysisDispatchModel
        The input model with input data
        from dispatcher

    dry_run: bool, Default True
        Dry run of analysis. If true,
        does not post results

    parameters
        The analysis model parameters

    """
    processing = construct_processing_record(
        analysis_dispatch_inputs, **parameters
    )
    if docdb_record_exists(processing):
        logger.info("Record already exists, skipping.")
        return

    # Execute analysis and write to results folder using the passed parameters.
    # Locate NWB files using s3fs under: {analysis_dispatch_inputs.s3_location}/nwb/*.nwb
    nwb_uri = discover_nwb_files_s3(analysis_dispatch_inputs.s3_location)
    
    if nwb_uri:
        logger.info(f"Found NWB file to process: {nwb_uri}")
        logger.info(f"Processing {nwb_uri}")
        # TODO: implement analysis read + compute, writing outputs into /results
        # nwbfile = ...
        # run_your_analysis(nwbfile, **parameters)
    else:
        logger.warning("No NWB file found, skipping processing.")

    # NOTE: This repository is a template; replace this loop with your real NWB I/O.
    # For example, for remote NWB you might use `pynwb.NWBHDF5IO` with a file-like
    # object from s3fs, or download locally before reading.
    # OR
    #     subprocess.run(["--param_1": parameters["param_1"]])

    processing.output_parameters = DynamicForagingModelFittingOutputs(
        isi_violations=["example_violation_1", "example_violation_2"],
        additional_info=(
            "This is an example of additional information about the analysis."
        ),
    )

    if not dry_run:
        logger.info("Running analysis and posting results")
        write_results_and_metadata(processing, ANALYSIS_BUCKET)
        logger.info("Successfully wrote record to docdb and s3")
    else:
        logger.info("Dry run complete. Results not posted")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    cli_cls = make_cli_model(DynamicForagingModelFittingSpecification)
    cli_model = cli_cls()
    logger.info(f"Command line args {cli_model.model_dump()}")
    input_model_paths = tuple(cli_model.input_directory.glob("job_dict/*"))
    logger.info(
        f"Found {len(input_model_paths)} input job models to run analysis on."
    )

    for model_path in input_model_paths:
        with open(model_path, "r") as f:
            analysis_dispatch_inputs = AnalysisDispatchModel.model_validate(
                json.load(f)
            )
        merged_parameters = get_analysis_model_parameters(
            analysis_dispatch_inputs,
            cli_model,
            DynamicForagingModelFittingSpecification,
            analysis_parameters_json_path=cli_model.input_directory
            / "analysis_parameters.json",
        )
        analysis_specification = (
            DynamicForagingModelFittingSpecification.model_validate(
                merged_parameters
            ).model_dump()
        )
        logger.info(f"Running with analysis specs {analysis_specification}")
        run_analysis(
            analysis_dispatch_inputs,
            bool(cli_model.dry_run),
            **analysis_specification,
        )
