#!/bin/bash
# Exit immediately if a command exits with a non-zero status.
set -e

# --- Windows Detection and Redirect ---
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    echo "Windows environment detected. Redirecting to install.bat..."
    cmd //c "install.bat $@"
    exit $?
fi

# --- macOS/Linux Installation Script ---

# Parse command-line options
REINSTALL=false
if [ "$1" == "--reinstall" ]; then
    REINSTALL=true
    echo "Reinstall mode enabled. Removing existing installations..."
fi

# Get the absolute path of the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Project directory: $PROJECT_DIR"

# --- Cleanup Function (for --reinstall) ---
cleanup_existing_installation() {
    echo "Cleaning up existing installation..."

    # Remove uv lockfile (for clean dependency resolution)
    UV_LOCK="$PROJECT_DIR/uv.lock"
    if [ -f "$UV_LOCK" ]; then
        rm -f "$UV_LOCK"
        echo "  Removed: $UV_LOCK"
    fi

    echo "Cleanup completed."
}

# Execute cleanup if reinstall mode is enabled
if [ "$REINSTALL" = true ]; then
    cleanup_existing_installation
fi

# --- Remove existing launcher script (Always executed) ---
echo "Removing existing launcher script..."

# Remove launcher script
LAUNCHER_PATH="$HOME/afterschool-survivors.sh"
if [ -f "$LAUNCHER_PATH" ]; then
    rm -f "$LAUNCHER_PATH"
    echo "  Removed: $LAUNCHER_PATH"
fi

# --- 1. Check for Python 3 ---
echo "Step 1: Checking for Python 3..."
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed. Please install Python 3 and try again." >&2
    exit 1
fi
echo "Python 3 found."

# --- 2. Check Python Version ---
echo "Step 2: Checking Python version..."
if [ -f "$PROJECT_DIR/.python-version" ]; then
    REQUIRED_VERSION=$(cat "$PROJECT_DIR/.python-version")
    # Get version from `python --version` which might be "Python 3.9.6"
    CURRENT_VERSION=$(python3 --version | awk '{print $2}')

    if [[ "$CURRENT_VERSION" != "$REQUIRED_VERSION" ]]; then
        echo "Warning: Required Python version is '$REQUIRED_VERSION', but you are using '$CURRENT_VERSION'."
        echo "Continuing installation, but compatibility issues may occur."
    else
        echo "Python version matches requirement ($REQUIRED_VERSION)."
    fi
else
    echo "Warning: .python-version file not found. Skipping version check."
fi

echo "Using Python command: python3"

# --- 3. Create Virtual Environment ---
VENV_DIR="$PROJECT_DIR/.venv"
echo "Step 3: Setting up virtual environment at $VENV_DIR..."
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists. Skipping creation."
else
    python3 -m venv "$VENV_DIR"
    echo "Virtual environment created."
fi

# --- 4. Activate Venv and Install/Update pip and uv ---
source "$VENV_DIR/bin/activate"
echo "Step 4: Setting up pip and uv build tool..."

# Ensure pip is installed in the virtual environment
if ! python3 -m pip --version &> /dev/null; then
    echo "pip not found in virtual environment. Installing pip..."
    # Download and install pip using ensurepip or get-pip.py
    if python3 -m ensurepip --upgrade &> /dev/null; then
        echo "pip installed via ensurepip."
    else
        echo "ensurepip failed. Downloading get-pip.py..."
        curl -sS https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
        python3 /tmp/get-pip.py
        rm /tmp/get-pip.py
        echo "pip installed via get-pip.py."
    fi
fi

# Upgrade pip and install uv
python3 -m pip install --upgrade pip
python3 -m pip install -U uv
echo "pip and uv installed."

# --- 5. Install Dependencies ---
echo "Step 5: Installing dependencies from pyproject.toml..."
# Change to project directory to ensure uv finds pyproject.toml
cd "$PROJECT_DIR"
uv sync
echo "Dependencies installed."

# --- 6. Create Launcher Script ---
LAUNCHER_NAME="afterschool-survivors.sh"
LAUNCHER_PATH="$HOME/$LAUNCHER_NAME"
echo "Step 6: Creating launcher script at $LAUNCHER_PATH..."

# Force overwrite if reinstall mode, otherwise check existence
if [ "$REINSTALL" = true ] || [ ! -f "$LAUNCHER_PATH" ]; then
    # Using a heredoc to write the script content
    cat << EOF > "$LAUNCHER_PATH"
#!/bin/bash
# This script activates the project's virtual environment and runs the main Python script.

# Absolute path to the project directory
PROJECT_DIR="$PROJECT_DIR"

# Activate the virtual environment
source "\$PROJECT_DIR/.venv/bin/activate"

# Change to the project directory to ensure relative paths work correctly
cd "\$PROJECT_DIR"

# Run the main application
python "src/main.py" "\$@"
EOF

    # Make the launcher script executable
    chmod +x "$LAUNCHER_PATH"
    echo "Launcher script created and made executable."
else
    echo "Launcher script already exists at $LAUNCHER_PATH. Skipping."
fi

# --- Completion Message ---
echo ""
echo "----------------------------------------"
echo "Installation Complete!"
echo "----------------------------------------"

if [ "$REINSTALL" = true ]; then
    echo "Reinstallation finished successfully."
    echo ""
    echo "Note: Virtual environment (.venv) was preserved."
    echo "      If you experience dependency issues, manually remove it:"
    echo "      rm -rf $PROJECT_DIR/.venv"
    echo "      Then run: ./install.sh"
    echo ""
fi

echo "To run the application, open a new terminal and type:"
echo "$LAUNCHER_NAME"
echo ""
echo "Or run directly from project directory:"
echo "  source .venv/bin/activate"
echo "  python src/main.py"
echo ""
echo "Optional: Add launcher to PATH for easier access"
echo "  Run this command to add to your shell configuration:"
echo "  echo 'export PATH=\"\$HOME:\$PATH\"' >> ~/.zshrc"
echo "  Then restart your terminal or run: source ~/.zshrc"
echo ""
echo "To reinstall (remove launcher before installing):"
echo "  ./install.sh --reinstall"
echo ""
