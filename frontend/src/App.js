import React, { useState, useEffect, useRef } from 'react';
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
  TableRow,
  IconButton,
  List,
  ListItem,
  Divider
} from '@mui/material';
import { styled } from '@mui/material/styles';
import BrainIcon from './assets/brain.png';
import GenerateIcon from './assets/generative.png';
import SuccessIcon from './assets/database-management.png';
import ErrorIcon from './assets/browser.png';
import EditIcon from '@mui/icons-material/Edit';
import CancelIcon from '@mui/icons-material/Cancel';
import SendIcon from '@mui/icons-material/Send';
import DownloadIcon from '@mui/icons-material/Download';
import { saveAs } from 'file-saver';

const BACKEND_URL = 'http://localhost:5000';

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  backgroundColor: '#f5f5f5',
  display: 'flex',
  gap: theme.spacing(2),
  alignItems: 'flex-start',
  maxWidth: '1200px',
  margin: '0 auto',
}));

const ChatContainer = styled(Box)(({ theme }) => ({
  height: 'calc(100vh - 180px)',
  overflowY: 'auto',
  padding: theme.spacing(2),
  backgroundColor: '#ffffff',
  borderRadius: theme.spacing(1),
  marginBottom: theme.spacing(2),
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
}));

const TableWrapper = styled(Box)(({ theme }) => ({
  maxHeight: '400px',
  overflowY: 'auto',
  border: '1px solid #e0e0e0',
  borderRadius: theme.spacing(1),
  '& .MuiTable-root': {
    borderCollapse: 'separate',
    borderSpacing: 0,
  },
  '& .MuiTableHead-root': {
    position: 'sticky',
    top: 0,
    backgroundColor: '#f5f5f5',
    zIndex: 1,
  },
  '& .MuiTableCell-head': {
    backgroundColor: '#f5f5f5',
    fontWeight: 'bold',
    borderBottom: '2px solid #e0e0e0',
  },
  '& .MuiTableCell-root': {
    padding: theme.spacing(1),
    whiteSpace: 'nowrap',
  },
}));

const InputContainer = styled(Box)(({ theme }) => ({
  position: 'fixed',
  bottom: 0,
  left: 0,
  right: 0,
  padding: theme.spacing(2),
  backgroundColor: '#ffffff',
  boxShadow: '0 -2px 4px rgba(0,0,0,0.1)',
  zIndex: 1000,
}));

const MessageBubble = styled(Box)(({ theme, isUser }) => ({
  maxWidth: '80%',
  padding: theme.spacing(2),
  marginBottom: theme.spacing(2),
  borderRadius: theme.spacing(2),
  backgroundColor: isUser ? '#e3f2fd' : '#f5f5f5',
  marginLeft: isUser ? 'auto' : 0,
  marginRight: isUser ? 0 : 'auto',
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
  const [messages, setMessages] = useState([]);
  const [schema, setSchema] = useState(null);
  const [schemaLoading, setSchemaLoading] = useState(true);
  const chatContainerRef = useRef(null);

  useEffect(() => {
    const fetchSchema = async () => {
      try {
        setSchemaLoading(true);
        const response = await fetch(`${BACKEND_URL}/api/schema`);
        if (!response.ok) {
          throw new Error('Failed to fetch schema');
        }
        const data = await response.json();
        if (data.database_schema && data.database_schema.tables) {
          setSchema(data.database_schema.tables);
        } else {
          throw new Error('Invalid schema format received');
        }
      } catch (err) {
        console.error('Schema loading error:', err);
        setError(err.message);
      } finally {
        setSchemaLoading(false);
      }
    };

    fetchSchema();
  }, []);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) {
      return; // Don't submit empty queries
    }

    setLoading(true);
    setError(null);

    // Add user message
    setMessages(prev => [...prev, { type: 'user', content: query }]);

    try {
      const response = await fetch(`${BACKEND_URL}/api/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query.trim() }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail);
      
      // Add system message with SQL
      setMessages(prev => [...prev, { 
        type: 'system', 
        content: 'Generated SQL Query:',
        sql: data.sql 
      }]);

      // Add data message
      setMessages(prev => [...prev, { 
        type: 'system', 
        content: 'Query Results:',
        data: data.data,
        columns: data.columns
      }]);

      // Add graph if available
      if (data.graph) {
        setMessages(prev => [...prev, { 
          type: 'system', 
          content: 'Data Visualization:',
          graph: data.graph
        }]);
      }
    } catch (err) {
      console.error('Query execution error:', err);
      setError(err.message);
      setMessages(prev => [...prev, { 
        type: 'error', 
        content: `Error: ${err.message}` 
      }]);
    } finally {
      setLoading(false);
      setQuery('');
    }
  };

  const handleDownloadCSV = async (data, columns) => {
    try {
      // Ask user for filename
      const filename = prompt('Enter filename for CSV download:', 'query_results.csv');
      if (!filename) return; // User cancelled

      // Ensure filename has .csv extension
      const finalFilename = filename.endsWith('.csv') ? filename : `${filename}.csv`;
      
      // Create a temporary link element
      const link = document.createElement('a');
      
      // Convert data to CSV
      const csvRows = [];
      // Add header
      csvRows.push(columns.join(','));
      // Add rows
      data.forEach(row => {
        csvRows.push(columns.map(col => JSON.stringify(row[col] ?? '')).join(','));
      });
      const csvString = csvRows.join('\n');
      
      // Create blob and URL
      const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8' });
      const url = window.URL.createObjectURL(blob);
      
      // Set up the link
      link.href = url;
      link.setAttribute('download', finalFilename);
      
      // Append to body, click, and remove
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Clean up
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading CSV:', error);
      alert('Failed to download CSV file');
    }
  };

  const renderMessage = (message) => {
    switch (message.type) {
      case 'user':
        return (
          <MessageBubble isUser>
            <Typography>{message.content}</Typography>
          </MessageBubble>
        );
      case 'system':
        return (
          <MessageBubble>
            <Typography variant="h6" gutterBottom>{message.content}</Typography>
            {message.sql && (
              <pre style={{ 
                backgroundColor: '#f8f9fa', 
                padding: '1rem',
                borderRadius: '4px',
                overflowX: 'auto',
                marginBottom: '1rem'
              }}>
                {message.sql}
              </pre>
            )}
            {message.data && message.columns && (
              <>
                <TableWrapper>
                  <TableContainer>
                    <Table size="small" stickyHeader>
                      <TableHead>
                        <TableRow>
                          {message.columns.map((column) => (
                            <TableCell key={column}>{column}</TableCell>
                          ))}
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {message.data.map((row, i) => (
                          <TableRow key={i}>
                            {message.columns.map((column) => (
                              <TableCell key={column}>{row[column]}</TableCell>
                            ))}
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </TableWrapper>
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                  <Button 
                    variant="contained"
                    color="primary"
                    onClick={() => handleDownloadCSV(message.data, message.columns)}
                    startIcon={<DownloadIcon />}
                  >
                    Download CSV
                  </Button>
                </Box>
              </>
            )}
            {message.graph && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                <img 
                  src={`data:image/png;base64,${message.graph}`}
                  alt="Data Visualization"
                  style={{ maxWidth: '100%', height: 'auto' }}
                />
              </Box>
            )}
          </MessageBubble>
        );
      case 'error':
        return (
          <MessageBubble>
            <Alert severity="error">{message.content}</Alert>
          </MessageBubble>
        );
      default:
        return null;
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (query.trim() && !loading && schema && !schemaLoading) {
        handleSubmit(e);
      }
    }
  };

  return (
    <Container maxWidth="lg" sx={{ height: '100vh', display: 'flex', flexDirection: 'column', pb: '80px' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', my: 2 }}>
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
        <Alert severity="error" sx={{ my: 2 }}>
          {error}
        </Alert>
      )}

      <ChatContainer ref={chatContainerRef}>
        {messages.map((message, index) => (
          <Box key={index}>
            {renderMessage(message)}
          </Box>
        ))}
        {loading && (
          <Box sx={{ display: 'flex', alignItems: 'center', my: 2 }}>
            <CircularProgress size={24} />
            <Typography sx={{ ml: 2 }}>Processing...</Typography>
          </Box>
        )}
      </ChatContainer>

      <InputContainer>
        <StyledPaper>
          <TextField
            fullWidth
            label="Enter your question"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            variant="outlined"
            disabled={loading}
            multiline
            rows={1}
            sx={{ 
              flex: 1,
              '& .MuiOutlinedInput-root': {
                height: '48px',
              }
            }}
          />
          <Button 
            type="submit" 
            variant="contained" 
            color="primary"
            disabled={loading || !query.trim()}
            onClick={handleSubmit}
            sx={{ 
              height: '48px',
              minWidth: '100px'
            }}
            endIcon={<SendIcon />}
          >
            Send
          </Button>
        </StyledPaper>
      </InputContainer>
    </Container>
  );
}

export default App; 