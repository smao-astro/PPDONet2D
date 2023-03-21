import argparse
import pathlib

import pandas as pd
import yaml

import onet_disk2D.run


def get_parser():
    parser = argparse.ArgumentParser()
    # IO
    parser.add_argument("--run_dir", type=str, required=True)
    parser.add_argument(
        "--args_file",
        type=str,
        default="args.yml",
        help="file that logs training args.",
    )
    parser.add_argument("--arg_groups_file", type=str, default="arg_groups.yml")
    parser.add_argument("--fargo_setup_file", type=str, default="fargo_setups.yml")
    parser.add_argument(
        "--model_dir",
        type=str,
        default="",
        help="Directory that store model files (params_struct.pkl, params.npy, etc). "
        "If empty, model_dir = run_dir. Use it for intermediate models in run_dir/xxx.",
    )
    # parameter
    parser.add_argument(
        "--parameter_file",
        type=str,
        help="pandas DataFrame file (csv) that keeps parameters to predict.",
    )

    parser.add_argument(
        "--save_dir", type=str, default="", help="If empty, save to train directory."
    )
    # inputs
    parser.add_argument("--radius_min", type=float)
    parser.add_argument("--radius_max", type=float)
    parser.add_argument(
        "--num_cell_radial",
        type=int,
        help="Predicted image's radial resolution (NY in fargo3d).",
    )
    parser.add_argument(
        "--num_cell_azimuthal",
        type=int,
        help="Predicted image's azimuthal resolution (NX in fargo3d).",
    )
    parser.add_argument(
        "--name", type=str, default="", help="Name attribute for output file."
    )

    return parser


def get_parameter_values(parameter_file):
    parameters = pd.read_csv(parameter_file, index_col=0)
    parameters = {k: series.values[..., None] for k, series in parameters.items()}
    return parameters


if __name__ == "__main__":
    predict_args = get_parser().parse_args()
    run_dir = pathlib.Path(predict_args.run_dir).resolve()
    if predict_args.model_dir:
        model_dir = pathlib.Path(predict_args.model_dir).resolve()
    else:
        model_dir = run_dir

    job_args = onet_disk2D.run.load_job_args(
        run_dir,
        predict_args.args_file,
        predict_args.arg_oups_file,
        predict_args.fargo_setup_file,
    )

    job = onet_disk2D.run.JOB(job_args)
    job.load_model(model_dir)

    save_dir = onet_disk2D.run.setup_save_dir(predict_args.save_dir, model_dir)

    # parameters
    parameter_values = get_parameter_values(predict_args.parameter_file)

    job.predict(
        parameters=parameter_values,
        save_dir=save_dir,
        ymin=predict_args.radius_min,
        ymax=predict_args.radius_max,
        ny=predict_args.num_cell_radial,
        nx=predict_args.num_cell_azimuthal,
        name=predict_args.name,
    )
