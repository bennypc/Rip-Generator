// This plugin will open a window to prompt the user to enter a number, and
// it will then create that many rectangles on the screen.

// This file holds the main code for plugins. Code in this file has access to
// the *figma document* via the figma global object.
// You can access browser APIs in the <script> tag inside "ui.html" which has a
// full browser environment (See https://www.figma.com/plugin-docs/how-plugins-run).

// This shows the HTML page in "ui.html".

figma.showUI(__html__, { width: 240, height: 180 });

figma.ui.onmessage = async (msg) => {
  if (msg.type === 'create-rip') {
    const nodes = figma.currentPage.selection;
    if (nodes.length === 0 || nodes[0].type !== 'VECTOR') {
      figma.ui.postMessage({
        type: 'error',
        message: 'Please select a vector object'
      });
      return;
    }

    const selectedNode = nodes[0];
    const svgPath = await selectedNode.exportAsync({ format: 'SVG' });

    const jaggednessValue = msg.jaggedness;

    try {
      const response = await fetch('http://127.0.0.1:5000/process-svg', {
        method: 'POST',
        body: JSON.stringify({
          svg_data: svgPath,
          jaggedness: jaggednessValue
        }),
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      if (data.status === 'success') {
        const rippedSVG = data.svg;

        // Convert the ripped SVG into a Figma node
        const frameNode = figma.createNodeFromSvg(rippedSVG);

        // Set the position to place the new SVG near the original
        frameNode.x = selectedNode.x + selectedNode.width + 10;
        frameNode.y = selectedNode.y;

        // Append this node to the current page
        figma.currentPage.appendChild(frameNode);

        figma.ui.postMessage({
          type: 'success',
          message: 'Rip created successfully'
        });
      } else {
        figma.ui.postMessage({
          type: 'error',
          message: data.message || 'Unknown error'
        });
      }
    } catch (error) {
      console.error('Error encountered:', error); // Log the entire error object

      if (error instanceof Error) {
        figma.ui.postMessage({
          type: 'error',
          message: `Failed to process SVG: ${error.message}`
        });
      } else {
        figma.ui.postMessage({
          type: 'error',
          message: `Failed to process SVG: ${JSON.stringify(error)}` // Try to stringify the error to see its content
        });
      }
    }
  }

  if (msg.type === 'cancel') {
    figma.closePlugin();
  }
};
