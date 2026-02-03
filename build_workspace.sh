#!/bin/bash
# Build and source the Go2 Mapping workspace

echo "Building Go2 Mapping workspace..."
cd /home/unitree/odom

# Build with symlink-install for faster iteration
colcon build --symlink-install

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Build successful!"
    echo ""
    echo "To use the package, run:"
    echo "  source /home/unitree/odom/install/setup.bash"
    echo ""
    echo "Or add to ~/.bashrc:"
    echo "  echo 'source /home/unitree/odom/install/setup.bash' >> ~/.bashrc"
    echo ""
else
    echo ""
    echo "✗ Build failed!"
    exit 1
fi
