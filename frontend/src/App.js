import React, { useState, useEffect } from 'react';
import { 
  Container, 
  TextField, 
  Button, 
  Paper, 
  Typography, 
  Box,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import { styled } from '@mui/material/styles';
import BrainIcon from './assets/brain.png';
import GenerateIcon from './assets/generative.png';
import ExecuteIcon from './assets/task-management.png';
import SuccessIcon from './assets/database-management.png';
import ErrorIcon from './assets/browser.png';
import { saveAs } from 'file-saver';

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  marginTop: theme.spacing(3),
  backgroundColor: '#f5f5f5',
}));

const Icon = styled('img')({
  width: '30px',
  height: '30px',
  marginRight: '10px',
});

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [schema, setSchema] = useState(null);
  const [schemaLoading, setSchemaLoading] = useState(true);

  useEffect(() => {
    const fetchSchema = async () => {
      try {
        setSchemaLoading(true);
        const response = await fetch('http://localhost:8005/api/schema');
        if (!response.ok) {
          throw new Error('Failed to fetch schema');
        }
        const data = await response.json();
        if (data.schema && data.schema.startsWith('Error:')) {
          throw new Error(data.schema);
        }
        setSchema(data.schema);
      } catch (err) {
        setError(err.message);
      } finally {
        setSchemaLoading(false);
      }
    };

    fetchSchema();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!schema) {
      setError('Database schema not available. Please check your connection.');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8005/api/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail);
      
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Helper to convert result to CSV
  const downloadCSV = () => {
    if (!result || !result.data || !result.columns) return;
    const csvRows = [];
    // Add header
    csvRows.push(result.columns.join(','));
    // Add rows
    result.data.forEach(row => {
      csvRows.push(result.columns.map(col => JSON.stringify(row[col] ?? '')).join(','));
    });
    const csvString = csvRows.join('\n');
    const blob = new Blob([csvString], { type: 'text/csv' });
    saveAs(blob, 'query_results.csv');
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ display: 'flex', alignItems: 'center', my: 3 }}>
        <Icon src={BrainIcon} alt="Brain" />
        <Typography variant="h4" component="h1">
          PostgreSQL Natural Language Query Assistant
        </Typography>
      </Box>

      {schemaLoading && (
        <Box sx={{ display: 'flex', alignItems: 'center', my: 2 }}>
          <CircularProgress size={24} />
          <Typography sx={{ ml: 2 }}>Loading database schema...</Typography>
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      <StyledPaper>
        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="Enter your question"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            margin="normal"
            variant="outlined"
            disabled={!schema || schemaLoading}
          />
          <Button 
            type="submit" 
            variant="contained" 
            color="primary"
            disabled={loading || !schema || schemaLoading}
            sx={{ mt: 2 }}
          >
            Generate SQL & Run
          </Button>
        </form>
      </StyledPaper>

      {loading && (
        <Box sx={{ display: 'flex', alignItems: 'center', my: 2 }}>
          <CircularProgress size={24} />
          <Typography sx={{ ml: 2 }}>Processing...</Typography>
        </Box>
      )}

      {result && (
        <>
          <StyledPaper sx={{ mt: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Icon src={GenerateIcon} alt="Generate" />
              <Typography variant="h6">Generated SQL</Typography>
            </Box>
            <pre style={{ 
              backgroundColor: '#f8f9fa', 
              padding: '1rem',
              borderRadius: '4px',
              overflowX: 'auto'
            }}>
              {result.sql}
            </pre>
          </StyledPaper>

          <StyledPaper sx={{ mt: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Icon src={SuccessIcon} alt="Success" />
              <Typography variant="h6">Query Results</Typography>
            </Box>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    {result.columns.map((column) => (
                      <TableCell key={column}>{column}</TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {result.data.map((row, i) => (
                    <TableRow key={i}>
                      {result.columns.map((column) => (
                        <TableCell key={column}>{row[column]}</TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
              <Button variant="outlined" color="primary" onClick={downloadCSV}>
                Download CSV
              </Button>
            </Box>
          </StyledPaper>
        </>
      )}
    </Container>
  );
}

export default App; 