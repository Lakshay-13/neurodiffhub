call env.bat
docker build -t %IMAGE_NAME% -f Dockerfile.dev .
docker run --rm --name %IMAGE_NAME% -ti -v "%cd%/:/app/" -p 3000:3000 %IMAGE_NAME%