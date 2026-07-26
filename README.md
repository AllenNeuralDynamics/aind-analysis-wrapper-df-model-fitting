# aind-analysis-wrapper-df-model-fitting

Maximum-likelihood-estimation (MLE) model fitting for Dynamic Foraging behavior, packaged as an
analysis wrapper capsule.

This capsule is built from
[aind-analysis-wrapper-template](https://github.com/AllenNeuralDynamics/aind-analysis-wrapper-template),
which is tracked as the `upstream` git remote. To pull in template changes:
`git fetch upstream && git merge upstream/main`.

The **analysis wrapper** is a standardized framework for running large-scale data analysis workflows on cloud infrastructure. It processes job input models from the [job dispatcher](https://github.com/AllenNeuralDynamics/aind-analysis-job-dispatch), executes your custom analysis code, and automatically handles metadata tracking and result storage.

### What it does

The analysis wrapper:
1. **Receives** job input models containing data file locations and analysis parameters
2. **Executes** your custom analysis code on the specified datasets
3. **Tracks** metadata including inputs, parameters, code versions, and execution details
4. **Stores** results to cloud storage and writes metadata records to a document database
5. **Prevents** duplicate processing by checking if analysis has already been completed

### What this capsule does

For each dispatched behavior session:
1. Discovers the NWB file under the asset's S3 location (`code/s3_nwb_util.py`)
2. Extracts choice and reward history, dropping ignored trials (sessions with fewer than 50 valid
   trials are skipped)
3. Fits the requested `aind_dynamic_foraging_models` forager
   (`code/dynamicforaging_mle_wrapper.py`)
4. Writes to `/results/`: `original_results_mle_fitting.json` (full fitting results),
   `fitted_session.png`, and `forager.pkl`
5. Returns a trimmed results dict — large entries such as latents, populations and per-fold
   cross-validation results are stripped before the record goes to DocDB

### Layout

| File | Purpose |
|---|---|
| `code/run_capsule.py` | Entrypoint; wires the models into `run_analysis_jobs` |
| `code/dynamicforaging_mle_model.py` | Input (`…Specification`) and output (`…Outputs`) pydantic models |
| `code/dynamicforaging_mle_wrapper.py` | The fitting itself |
| `code/s3_nwb_util.py` | Locating NWB files on S3 |
| `code/settings.env` | Non-secret configuration (DocDB collection, analysis bucket, …) |
| `data/job_dict/example_dispatch_job.json` | Example dispatcher input for local testing |

### Environment Setup
Configuration lives in `/code/settings.env` — the DocDB collection and analysis bucket for this
capsule are already set there. Secrets (`CODEOCEAN_API_TOKEN`, `CODEOCEAN_EMAIL`, and the AWS
assumable role) are set in the capsule settings, not in this file.

### Analysis parameters
Parameters are validated against `DynamicForagingModelFittingSpecification`. They are resolved by
`analysis-pipeline-utils` in this order, later winning:

1. `analysis_code.parameters` in the dispatch job
2. app-panel / CLI overrides
3. `distributed_parameters` in the dispatch job

`agent_class`, `agent_kwargs` and `fit_kwargs` are what the dispatcher varies per job;
`analysis_name` and `analysis_tag` carry defaults and mainly exist to tag results for querying.

### Running Analysis and Storing Output
The analysis is executed in **`run_analysis`** in `run_capsule.py`. An example of the input model
passed in can be found in `/data/job_dict/example_dispatch_job.json`.

* **Users can also add an app panel for input arguments that are part of the analysis model**.

* **Run_analysis should return the output parameters AND results should be written to **`/results/`** folder in the capsule**. The results folder will then be copied to the S3 Analysis Bucket path set in `settings.env`. This path will then be stored as part of the metadata record that will get written to the document database and can be queried later on.

* The metadata record is a combination of input data, analysis parameters, git commits, etc. All of these are used to query if analysis has already been run on the combination of input data, parameters, etc. ***IMPORTANT***: **BE SURE TO COMMIT ALL CHANGES IN THIS CAPSULE. IF CHANGES ARE NOT COMMITED AND ANALYSIS NEEDS TO BE RUN, IT COULD BE SKIPPED IF THE METADATA RECORD ALREADY EXISTS FOR THE GIVEN COMBINATION OF INPUT DATA, ANALYSIS PARAMETERS, CODE, ETC**

  Jobs whose record already exists are skipped, and a `/results/skip_<job>` marker file is written
  so the pipeline step does not fail.

### Testing Analysis Wrapper
To test and run at the pipeline level, a reproducible run needs to be executed. **When ready to run analysis and post results, be sure to set the dry run flag in the app panel to 0 so the results are posted. By default, dry run is enabled.**.
