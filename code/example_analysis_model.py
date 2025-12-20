"""
This is an example of an analysis-specific schema
for the parameters required by that analysis
"""
from pydantic import Field
from typing import List, Optional, Union

from aind_data_schema.base import GenericModel

class DynamicForagingModelFittingSpecification(GenericModel):
    """
    Represents the specification for an analysis, including its name,
    version, libraries to track, and parameters.
    """

    analysis_name: str = Field(
        default="MLE fitting",
        description="User-defined name for the analysis"
    )
    analysis_tag: str = Field(
        ...,
        description=(
            "User-defined tag to organize results "
            "for querying analysis output",
        ),

    )

    # Top-level analysis parameters
    agent_class: Optional[str] = Field(
        default="ForagerLossCounting",
        description="Agent class to use for model fitting",
    )

    agent_kwargs: Optional[dict] = Field(
        default_factory=lambda: {
            "win_stay_lose_switch": True,
            "choice_kernel": "none",
        },
        description=(
            "Top-level agent keyword arguments"
        ),
    )

    fit_kwargs: Optional[dict] = Field(
        default_factory=lambda: {
            "DE_kwargs": {"polish": True, "seed": 42},
            "k_fold_cross_validation": 10,
        },
        description=(
            "Top-level fitting keyword arguments."
        ),
    )



class DynamicForagingModelFittingOutputs(GenericModel):
    """
    Represents the outputs of an analysis, including a list of ISI violations.
    """

    
    additional_info: Optional[str] = Field(
        default=None, description="Additional information about the analysis"
    )

    # Arbitrary fitting results (e.g., parameters, metrics). Stored as a dict.
    fitting_results: Optional[dict] = Field(
        default=None,
        description=(
            "Arbitrary dictionary containing fitting results such as estimated "
            "parameters and metrics."
        ),
    )

