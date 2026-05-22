"""Central registry of Physical Systems solver metadata and inference schemas."""

from __future__ import annotations

from typing import Any, Literal

from khukra.domains.physical.core import (
    EquationSpec,
    SolverOutput,
    SolverParameter,
    SolverSpec,
    SolverVariable,
)

ModelKind = Literal["solver", "dynamic_simulation", "forecast", "surrogate_candidate"]
ArtifactRole = Literal[
    "solver_output",
    "simulation_trace",
    "sweep_dataset",
    "surrogate_training_dataset",
    "research_trace",
]

MODEL_KINDS: tuple[ModelKind, ...] = (
    "solver",
    "dynamic_simulation",
    "forecast",
    "surrogate_candidate",
)

ARTIFACT_ROLES: tuple[ArtifactRole, ...] = (
    "solver_output",
    "simulation_trace",
    "sweep_dataset",
    "surrogate_training_dataset",
    "research_trace",
)

# model_id -> model_kind
MODEL_CLASSIFICATION: dict[str, ModelKind] = {
    "cantilever_beam": "solver",
    "damped_oscillator": "dynamic_simulation",
    "counterflow_heat_exchanger": "solver",
    "point_mass_2d": "dynamic_simulation",
}

DEFAULT_ARTIFACT_ROLE: dict[str, ArtifactRole] = {
    "cantilever_beam": "solver_output",
    "damped_oscillator": "simulation_trace",
    "counterflow_heat_exchanger": "solver_output",
    "point_mass_2d": "simulation_trace",
}

_BEAM_EQUATIONS = [
    EquationSpec(
        name="deflection",
        form="w(x) = q*x^2*(6*L^2 - 3*L*x + x^2) / (24*E*I)",
        variables=["x", "w"],
        parameters=["q", "L", "E", "I"],
        equation_type="algebraic",
        description="Euler-Bernoulli transverse deflection under uniform load",
    ),
    EquationSpec(
        name="bending_moment",
        form="M(x) = q*x^2*(L - x) / 2",
        variables=["x", "M"],
        parameters=["q", "L"],
        equation_type="algebraic",
        description="Internal bending moment distribution",
    ),
]

_OSCILLATOR_EQUATIONS = [
    EquationSpec(
        name="equation_of_motion",
        form="m*x'' + c*x' + k*x = 0",
        variables=["x", "x_dot"],
        parameters=["m", "c", "k"],
        equation_type="ode",
        residual="m*x_ddot + c*x_dot + k*x",
        description="Linear damped harmonic oscillator",
    ),
]

_HEAT_EXCHANGER_EQUATIONS = [
    EquationSpec(
        name="hot_energy_balance",
        form="C_h * dT_h/dt = -UA * (T_h - T_c)",
        variables=["T_h", "T_c"],
        parameters=["C_h", "UA"],
        equation_type="ode",
        residual="C_h*T_h_dot + UA*(T_h - T_c)",
        description="Hot-side lumped capacitance balance",
    ),
    EquationSpec(
        name="cold_energy_balance",
        form="C_c * dT_c/dt = UA * (T_h - T_c)",
        variables=["T_h", "T_c"],
        parameters=["C_c", "UA"],
        equation_type="ode",
        residual="C_c*T_c_dot - UA*(T_h - T_c)",
        description="Cold-side lumped capacitance balance",
    ),
]

_POINT_MASS_EQUATIONS = [
    EquationSpec(
        name="horizontal_dynamics",
        form="m * dv_x/dt = F_x - k_drag * v * v_x",
        variables=["v_x", "x"],
        parameters=["m", "F_x", "k_drag"],
        equation_type="ode",
        description="Horizontal point-mass with quadratic drag",
    ),
    EquationSpec(
        name="vertical_dynamics",
        form="m * dv_z/dt = F_z - k_drag * v * v_z - m*g",
        variables=["v_z", "z"],
        parameters=["m", "F_z", "k_drag", "g"],
        equation_type="ode",
        description="Vertical point-mass with gravity and drag",
    ),
]

SOLVER_SPECS: dict[str, SolverSpec] = {
    "cantilever_beam": SolverSpec(
        model_id="cantilever_beam",
        subdomain="mechanics",
        model_kind="solver",
        title="Cantilever beam (Euler-Bernoulli)",
        governing_equations="w(x) = q x^2 (6L^2 - 3Lx + x^2) / (24 E I); M(x) = q x^2 (L-x)/2",
        assumptions=[
            "Uniform distributed load",
            "Linear elastic Euler-Bernoulli beam",
            "Small deflections",
        ],
        parameters=[
            SolverParameter("length", "m", 5.0, "Beam span"),
            SolverParameter("youngs_modulus", "Pa", 210e9, "Elastic modulus"),
            SolverParameter("second_moment", "m^4", 3.4e-6, "Second moment of area"),
            SolverParameter("load", "N/m", 1200.0, "Distributed load"),
            SolverParameter("points", "", 100, "Spatial discretization count"),
        ],
        state_variables=[
            SolverVariable("position_m", "m", "spatial", "Span coordinate"),
            SolverVariable("deflection_mm", "mm", "derived", "Transverse deflection"),
        ],
        outputs=[
            SolverOutput("max_deflection_mm", "mm", "Max deflection"),
            SolverOutput("peak_deflection_mm", "mm", "Peak deflection along span"),
            SolverOutput("max_moment_knm", "kN*m", "Max bending moment"),
            SolverOutput("tip_deflection_mm", "mm", "Tip deflection"),
        ],
        equations=_BEAM_EQUATIONS,
        predictor_type="mechanics_beam_solver",
        artifact_role="solver_output",
    ),
    "damped_oscillator": SolverSpec(
        model_id="damped_oscillator",
        subdomain="mechanics",
        model_kind="dynamic_simulation",
        title="Damped mass-spring oscillator",
        governing_equations="m x'' + c x' + k x = 0",
        assumptions=["Linear spring and viscous damper", "No external forcing"],
        parameters=[
            SolverParameter("mass", "kg", 1.0, "Mass"),
            SolverParameter("damping", "N*s/m", 0.5, "Damping coefficient"),
            SolverParameter("stiffness", "N/m", 4.0, "Spring stiffness"),
            SolverParameter("initial_displacement", "m", 1.0, "Initial displacement"),
            SolverParameter("initial_velocity", "m/s", 0.0, "Initial velocity"),
            SolverParameter("duration", "s", 10.0, "Simulation duration"),
            SolverParameter("dt", "s", 0.05, "Output time step"),
        ],
        state_variables=[
            SolverVariable("displacement", "m", "state", "Position"),
            SolverVariable("velocity", "m/s", "state", "Velocity"),
            SolverVariable("energy", "J", "derived", "Mechanical energy"),
        ],
        outputs=[
            SolverOutput("peak_displacement", "m", "Peak displacement"),
            SolverOutput("final_energy", "J", "Final energy"),
            SolverOutput("settling_time", "s", "Settling time"),
        ],
        equations=_OSCILLATOR_EQUATIONS,
        predictor_type="mechanics_dynamic_simulation",
        artifact_role="simulation_trace",
    ),
    "counterflow_heat_exchanger": SolverSpec(
        model_id="counterflow_heat_exchanger",
        subdomain="thermofluid",
        model_kind="solver",
        title="Counterflow heat exchanger (lumped NTU)",
        governing_equations="C_h dT_h/dt = -UA(T_h-T_c); C_c dT_c/dt = UA(T_h-T_c)",
        assumptions=["Lumped capacitance", "Constant UA", "Counterflow effectiveness correlation"],
        parameters=[
            SolverParameter("hot_inlet_c", "deg C", 90.0, "Hot inlet temperature"),
            SolverParameter("cold_inlet_c", "deg C", 20.0, "Cold inlet temperature"),
            SolverParameter("hot_capacity", "W/K", 5000.0, "Hot-side heat capacity rate"),
            SolverParameter("cold_capacity", "W/K", 4500.0, "Cold-side heat capacity rate"),
            SolverParameter("ua_w_per_k", "W/K", 800.0, "Overall heat transfer coefficient"),
            SolverParameter("duration_s", "s", 600.0, "Simulation duration"),
            SolverParameter("dt", "s", 1.0, "Output time step"),
        ],
        state_variables=[
            SolverVariable("hot_temp_c", "deg C", "state", "Hot fluid temperature"),
            SolverVariable("cold_temp_c", "deg C", "state", "Cold fluid temperature"),
        ],
        outputs=[
            SolverOutput("ntu", "", "Number of transfer units"),
            SolverOutput("effectiveness", "", "Heat exchanger effectiveness"),
            SolverOutput("steady_hot_outlet_c", "deg C", "Hot outlet temperature"),
            SolverOutput("steady_cold_outlet_c", "deg C", "Cold outlet temperature"),
            SolverOutput("peak_heat_transfer_kw", "kW", "Peak heat transfer rate"),
            SolverOutput("hot_outlet_steady_error", "", "Hot outlet steady-state error"),
        ],
        equations=_HEAT_EXCHANGER_EQUATIONS,
        predictor_type="thermofluid_heat_exchanger_solver",
        artifact_role="solver_output",
    ),
    "point_mass_2d": SolverSpec(
        model_id="point_mass_2d",
        subdomain="dynamics",
        model_kind="dynamic_simulation",
        title="2D point-mass with applied force and drag",
        governing_equations="m dv/dt = F_applied - F_drag - mg (vertical)",
        assumptions=[
            "Point mass in vertical plane",
            "Quadratic speed-dependent drag",
            "Constant applied force magnitude and angle",
        ],
        parameters=[
            SolverParameter("mass_kg", "kg", 25.0, "Mass"),
            SolverParameter("applied_force_n", "N", 350.0, "Applied force magnitude"),
            SolverParameter("force_angle_deg", "deg", 15.0, "Force angle from horizontal"),
            SolverParameter("drag_coeff", "", 0.08, "Quadratic drag coefficient"),
            SolverParameter("initial_height_m", "m", 100.0, "Initial vertical position"),
            SolverParameter("initial_speed_mps", "m/s", 20.0, "Initial horizontal speed"),
            SolverParameter("duration_s", "s", 30.0, "Simulation duration"),
            SolverParameter("dt", "s", 0.1, "Output time step"),
        ],
        state_variables=[
            SolverVariable("position_x_m", "m", "state", "Horizontal position"),
            SolverVariable("position_z_m", "m", "state", "Vertical position"),
            SolverVariable("speed_mps", "m/s", "derived", "Speed magnitude"),
        ],
        outputs=[
            SolverOutput("max_height_m", "m", "Maximum height"),
            SolverOutput("max_speed_mps", "m/s", "Maximum speed"),
            SolverOutput("displacement_x_m", "m", "Horizontal displacement"),
            SolverOutput("final_height_m", "m", "Final height"),
        ],
        equations=_POINT_MASS_EQUATIONS,
        predictor_type="dynamics_point_mass_simulation",
        artifact_role="simulation_trace",
    ),
}


def workbench_model_entry(model_id: str) -> dict[str, Any] | None:
    """Compact workbench payload for a single solver (catalog + UI)."""
    spec = SOLVER_SPECS.get(model_id)
    if not spec:
        return None
    meta = spec.to_metadata()["solver_spec"]
    return {
        "model_id": model_id,
        "subdomain": spec.subdomain,
        "model_kind": spec.model_kind,
        "title": spec.title,
        "predictor_type": spec.predictor_type,
        "artifact_role": spec.artifact_role,
        "solver_spec": meta,
        "output_names": [o.name for o in spec.outputs],
        "series_names": [v.name for v in spec.state_variables],
    }


def list_workbench_models() -> list[dict[str, Any]]:
    """All physical solvers grouped for workbench UI."""
    return [workbench_model_entry(mid) for mid in SOLVER_SPECS if workbench_model_entry(mid)]


def catalog_parameters_for(model_id: str, infer_type) -> list[dict[str, Any]] | None:
    """Build catalog ParameterSchema dicts from SolverSpec when available."""
    from khukra.domains.physical.units import parameter_schema_from_solver_param

    spec = SOLVER_SPECS.get(model_id)
    if not spec:
        return None
    rows: list[dict[str, Any]] = []
    for p in spec.parameters:
        rows.append(
            parameter_schema_from_solver_param(
                p.name,
                infer_type(p.default),
                p.default,
                p.name.replace("_", " ").title(),
                unit=p.unit,
                description=p.description,
            )
        )
    return rows


def model_kind(model_id: str) -> ModelKind:
    return MODEL_CLASSIFICATION.get(model_id, "solver")


def artifact_role(model_id: str) -> ArtifactRole:
    return DEFAULT_ARTIFACT_ROLE.get(model_id, "solver_output")


def get_solver_spec(model_id: str) -> SolverSpec | None:
    return SOLVER_SPECS.get(model_id)


def inference_meta_for(model_id: str) -> dict[str, Any]:
    """Build inference registry entry from central solver spec."""
    spec = SOLVER_SPECS.get(model_id)
    if not spec:
        return {}
    return {
        "type": spec.predictor_type,
        "version": spec.version,
        "uncertainty": spec.supports_uncertainty,
        "model_kind": spec.model_kind,
        "outputs": [(o.name, o.label, o.unit) for o in spec.outputs],
    }
