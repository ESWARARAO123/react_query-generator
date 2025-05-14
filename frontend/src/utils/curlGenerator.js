// Remove the child_process import as it's not available in browser
// const { exec } = require('child_process');

export const generateCurlCommand = (query) => {
  const apiUrl = 'http://localhost:5000/api/execute';
  const curlCommand = `curl -X POST ${apiUrl} \\
  -H "Content-Type: application/json" \\
  -d '{"query": "${query.replace(/"/g, '\\"')}"}'`;
  
  // Print to terminal-style output in browser console
  console.log('\n=== API Request Details ===');
  console.log(`Endpoint: ${apiUrl}`);
  console.log('CURL Command to run in terminal:');
  console.log(curlCommand);
  console.log('===========================\n');
  
  return curlCommand;
};

export const executeCurlCommand = async (query) => {
  try {
    // Generate and display the curl command
    const curlCommand = generateCurlCommand(query);

    // Make the actual API call using fetch
    const response = await fetch('http://localhost:5000/api/execute', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ query }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to execute query');
    }

    // Print the response data to console
    console.log('\n=== API Response ===');
    console.log('Generated SQL:', data.sql);
    console.log('Results:', JSON.stringify(data.data, null, 2));
    console.log('===================\n');

    return data;
  } catch (error) {
    console.log('\n=== Error ===');
    console.error('API Error:', error.message);
    console.log('=============\n');
    throw new Error('Failed to execute query: ' + error.message);
  }
};