# autobfx

[![Tests](https://github.com/Ulthran/autobfx/actions/workflows/routine_tests.yaml/badge.svg)](https://github.com/Ulthran/autobfx/actions/workflows/routine_tests.yaml)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/5c72b0d1e63e4efd8e6fcca22708b506)](https://app.codacy.com/gh/Ulthran/autobfx/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![codecov](https://codecov.io/gh/Ulthran/autobfx/graph/badge.svg?token=P8XruywW8Q)](https://codecov.io/gh/Ulthran/autobfx)

To suite the AI hype: have a simple, pretrained LLM optionally look through logs and benchmarks to assess if anything went wrong but unnoticed and how efficient the pipeline was

## NOTES IN DEV

Run a flow directly: `python flows/flow_name.py /path/to/project/`
Supported workflows:
-  Running a whole pipeline (e.g. qc & decontam) on a set of samples (run pipeline flow) `python /path/to/qc.py projects/example`
-  Running a whole pipeline on a single sample (run pipeline flow with defined `samples`) `python /path/to/qc.py projects/example --samples tests/data/reads/LONG_R1.fastq.gz`
-  Running a single step on a set of samples (run flow) `python /path/to/fastqc.py projects/example`
-  Running a single step on a single sample (run flow with defined `samples`) `python /path/to/fastqc.py projects/example --samples tests/data/reads/LONG_R1.fastq.gz`

## TODO

-  Conda manager (docker should be easy, singularity might not be)
  -  Do we not bother? Just let users manage this
-  DAG-esque thing to know what work to do and not to do (marker files?)

## Getting started

After `git clone`ing the repo, run `python -m venv env/` to create a virtual environment, `source env/bin/activate` to activate it, and `pip install -r requirements.txt` to install the necessary packages. Then open up one terminal and start the prefect server with `prefect server start` (it'll show a message and then keep running until you cancel it, leave it running until you're done with AutoBfx), open another terminal and start a local work pool with `prefect work-pool create default` (creating a work pool named `default`) then run  (again, leave it running), and open a third terminal 

## The workflow

### Sample Collection

In the first stage, we need to collect our input data and maintain an appropriate amount of metadata to be able to track results back to where they came from once we get to downstream analysis.

-  Point to files/directories/URIs with analysis inputs
-  Collect these inputs into a unified location and record where and when they are from
-  Collate all the relevant metadata and make sure there isn't aren't any important overlapping indeces/names/etc
 
### Preprocess-Setup-Run-Postprocess (PSRP) Loop

Each step in the workflow is composed of four parts:

-  Preprocess
  -  Prepare the inputs for being processed with whatever tool we use in the `Run` step (e.g. reformatting, renaming, combining, etc)
-  Setup
  -  Prepare the tool itself to be run (e.g. create the necessary environments, pull images, download databases, etc)
-  Run
  -  Run the tool
-  Postprocess
  -  Do any postprocessing on the outputs that feels necessary (e.g. reformatting, clean up auxilliary files, combining, etc)
  -  If there are any kinds of checks to perform on the outputs to make sure they are legit or fit expectations this is a good time to run those. Any standard simple analyses that might come in handy down the line as well. Especially if the outputs include large files that you want to get rid of once they've been used in downstream steps.
  -  In a multi-PSRP loop, the postprocess and preprocess stages can have a tendency to sort of merge together. In general, lean towards keeping things grouped around which tool they apply to most but there aren't any particularly strict standards here.