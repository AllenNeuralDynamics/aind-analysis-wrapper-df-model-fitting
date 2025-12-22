import logging
from typing import Iterable, List, Optional, Sequence, Union

logger = logging.getLogger(__name__)


def _normalize_s3_prefix(path: str) -> str:
    """Normalize S3 prefix strings for consistent globbing.

    Accepts prefixes like:
    - s3://bucket/prefix
    - bucket/prefix

    Returns the path without the leading s3:// and without trailing slashes.
    """
    if not isinstance(path, str) or not path.strip():
        raise ValueError("s3_location must be a non-empty string")
    p = path.strip()
    if p.startswith("s3://"):
        p = p[len("s3://") :]
    return p.rstrip("/")


def discover_nwb_files_s3(
    s3_location: Union[str, Sequence[str]],
    *,
    fs=None,
) -> Optional[str]:
    """Locate NWB files under `{s3_location}/nwb/*.nwb` using s3fs.

    Parameters
    ----------
    s3_location:
        A single S3 prefix (string) or a list/tuple of prefixes.
        Each prefix may be `s3://bucket/prefix` or `bucket/prefix`.

    fs:
        Optional filesystem object (e.g. `s3fs.S3FileSystem`) for testability.

    Returns
    -------
    Optional[str]
        The `s3://...` URI to the `*.nwb` file found, or None if not found.
    """
    if isinstance(s3_location, str):
        prefixes: Iterable[str] = [s3_location]
    else:
        prefixes = s3_location

    # Import lazily so the module can be imported even if the env is missing s3fs.
    if fs is None:
        import s3fs  # type: ignore

        fs = s3fs.S3FileSystem(anon=False)

    results: List[str] = []
    for prefix in prefixes:
        norm = _normalize_s3_prefix(prefix)
        if norm.endswith(".nwb"):
            matches = fs.glob(norm) or []
        else:
            pattern = f"{norm}/nwb/*.nwb"
            matches = fs.glob(pattern) or []
        # s3fs returns paths without s3://, normalize to URIs for downstream.
        results.extend([f"s3://{m}" if not str(m).startswith("s3://") else str(m) for m in matches])

    unique_results = sorted(set(results))

    if not unique_results:
        logger.warning(f"No NWB files found in {s3_location}")
        return None
    elif len(unique_results) > 1:
        logger.warning(
            f"More than one NWB file found in {s3_location}. "
            f"Returning the first one: {unique_results[0]}"
        )
        return unique_results[0]

    return unique_results[0]


def get_history_from_nwb(nwb):
    """Get choice and reward history from nwb file
    
    #TODO move this to aind-behavior-nwb-util
    """

    df_trial = nwb.trials.to_dataframe()

    autowater_offered = (df_trial.auto_waterL == 1) | (df_trial.auto_waterR == 1)
    choice_history = df_trial.animal_response.map({0: 0, 1: 1, 2: np.nan}).values
    reward_history = df_trial.rewarded_historyL | df_trial.rewarded_historyR
    p_reward = [
        df_trial.reward_probabilityL.values,
        df_trial.reward_probabilityR.values,
    ]
    random_number = [
        df_trial.reward_random_number_left.values,
        df_trial.reward_random_number_right.values,
    ]

    baiting = False if "without baiting" in nwb.protocol.lower() else True

    return (
        baiting,
        choice_history,
        reward_history,
        p_reward,
        autowater_offered,
        random_number,
    )