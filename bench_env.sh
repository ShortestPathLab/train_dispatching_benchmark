if [[ "${BASH_SOURCE[0]}" = "${0}" ]]; then
	>&2 echo "Remember: you need to run me as 'source ${0}', not execute it!"
	exit
fi

# Create or activate Python virtual environment
if [ -d .venv ]; then
	source .venv/bin/activate
else
	uv sync
	source .venv/bin/activate
fi

# Download MiniZinc Distribution if required
if [ ! -f minizinc ]; then
	wget https://github.com/MiniZinc/MiniZincIDE/releases/download/edge/MiniZincIDE-build1700270071-x86_64.AppImage
	mv MiniZincIDE-*.AppImage minizinc
	chmod +x minizinc
fi
# Source the MiniZinc Distribution
export PATH=$(pwd):$PATH

# Set other environment variables and load cluster modules
module load CpoFzn/1.0.0
module load Gurobi/12.0.1

# module load MiniZinc/2.9.0
# module load Chuffed/0f253d1f2fa60a3f991f428c249b8af95a03dbbf
# module load OR-Tools/9.12.4544
