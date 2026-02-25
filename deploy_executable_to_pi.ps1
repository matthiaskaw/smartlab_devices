# Deploy SmartLab to Raspberry Pi
# This script deploys the published application to a Raspberry Pi


$REMOTE_USER = "smartlab"
$REMOTE_HOST = "192.168.0.100"
$REMOTE_PATH = "~/devices"
#$REMOTE_SSH_KEY = "c:\Users\matth\.ssh\smartlab_pi_4"
$REMOTE_SSH_KEY = "c:\Users\da72seda\.ssh\smartlab_pi_4"


$WSL_HOST = $REMOTE_HOST
$WSL_SSH_KEY = $REMOTE_SSH_KEY
$WSL_USER = $REMOTE_USER
$WSL_TARGET_PATH = $REMOTE_PATH


$EXECUTABLE_NAME = "smps"
$LOCAL_EXECUTABLE = "./dist/${EXECUTABLE_NAME}"

$LOCAL_PYTHON_SCRIPT = "./smps.py"
$LOCAL_SRC_DIR = "./src/*.py"


Write-Host "Copying files to wsl..." -ForegroundColor Yellow
ssh -i "${WSL_SSH_KEY}" "${WSL_USER}@${WSL_HOST}" "mkdir ${WSL_TARGET_PATH}/src"
scp -i "${WSL_SSH_KEY}" "${LOCAL_SRC_DIR}" "${WSL_USER}@${WSL_HOST}:${WSL_TARGET_PATH}/src/"
scp -i "${WSL_SSH_KEY}" "${LOCAL_PYTHON_SCRIPT}" "${WSL_USER}@${WSL_HOST}:${WSL_TARGET_PATH}"

Write-Host "Files successfully copied to WSL!" -ForegroundColor Green


Write-Host "Building executable for linux..." -ForegroundColor Yellow

ssh -i "${WSL_SSH_KEY}" "${WSL_USER}@${WSL_HOST}" "source venv/bin/activate && cd ${WSL_TARGET_PATH} && pyinstaller --onefile -n ${EXECUTABLE_NAME} ${WSL_TARGET_PATH}/${LOCAL_PYTHON_SCRIPT}"

# Write-Host "Venv started successfully..." -ForegroundColor Green

# if ($LASTEXITCODE -ne 0) {
#     Write-Host "Error: Failed to start venv" -ForegroundColor Red
#     exit 1
# }

# Write-Host "Getting executable from WSL..." -ForegroundColor Yellow

# scp -i "${WSL_SSH_KEY}" "${WSL_USER}@${WSL_HOST}:${WSL_TARGET_PATH}/dist/${EXECUTABLE_NAME}" ".\dist\" 

# if ($LASTEXITCODE -ne 0) {
#     Write-Host "Error: Failed to get executable..." -ForegroundColor Red
#     exit 1
# }



# Write-Host "Sending executable to Remote Host..." -ForegroundColor Yellow
# scp -i "${REMOTE_SSH_KEY}" "${LOCAL_EXECUTABLE}" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}"

# ssh -i "${REMOTE_SSH_KEY}" "${REMOTE_USER}@${REMOTE_HOST}" "chmod +x ${REMOTE_PATH}/${EXECUTABLE_NAME}"


