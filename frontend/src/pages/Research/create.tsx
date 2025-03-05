import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import {
  Alert,
  Box,
  Button,
  Chip,
  Container,
  Divider,
  FormControl,
  FormHelperText,
  Grid2,
  IconButton,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  SelectChangeEvent,
  Snackbar,
  TextField,
  Typography,
  CircularProgress,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import { encoding_for_model, type TiktokenModel, type Tiktoken } from 'tiktoken';
import debounce from 'lodash/debounce';

import Header from '../../components/common/Header';
import NavBar from '../../components/common/NavBar';
import Footer from '../../components/common/Footer';
import { useApi } from '../../hooks/useApi';
import { ResearchService, AiModel } from '../../types/research_service';
import { ResearchJob, ResearchJobCreateResponse, ResearchJobStatus } from '../../types/research_job';

interface ModelParam {
  key: string;
  value: string;
}

const CreateResearchJobPage: React.FC = () => {
  const { researchServicesApi, researchJobsApi } = useApi();
  
  // Form state
  const [services, setServices] = useState<ResearchService[]>([]);
  const [selectedService, setSelectedService] = useState<string>('');
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [prompt, setPrompt] = useState<string>('');
  const [modelParams, setModelParams] = useState<ModelParam[]>([{ key: '', value: '' }]);
  
  // UI state
  const [loading, setLoading] = useState<boolean>(false);
  const [loadingServices, setLoadingServices] = useState<boolean>(true);
  const [tokenCount, setTokenCount] = useState<number>(0);
  const [maxTokens, setMaxTokens] = useState<number>(0);
  
  // Error handling state
  const [tokenCountError, setTokenCountError] = useState<string | null>(null);
  const [jobCreationError, setJobCreationError] = useState<string | null>(null);
  const [showError, setShowError] = useState<boolean>(false);

  // Follow-up questions state
  const [questions, setQuestions] = useState<string[]>([]);
  const [answers, setAnswers] = useState<string[]>([]);
  const [createdJob, setCreatedJob] = useState<ResearchJob | null>(null);
  const [isAnswering, setIsAnswering] = useState<boolean>(false);
  const [isPollActive, setIsPollActive] = useState<boolean>(false);
  const [pollInterval, setPollInterval] = useState<NodeJS.Timeout | null>(null);

  // Keep track of which models are supported by tiktoken
  const [tiktokenSupportedModels, setTiktokenSupportedModels] = useState<Record<string, boolean>>({});

  // Load services on component mount
  useEffect(() => {
    const fetchServices = async () => {
      try {
        setLoadingServices(true);
        const servicesData = await researchServicesApi.getResearchServices();
        setServices(servicesData);
        
        // Check which models are supported by tiktoken
        const supportedModels: Record<string, boolean> = {};
        servicesData.forEach(service => {
          service.service_models.forEach(sm => {
            try {
              // Just try to create an encoder for the model to see if it's supported
              sm.model.model_key as TiktokenModel;
              supportedModels[sm.model.model_key] = true;
            } catch (error) {
              supportedModels[sm.model.model_key] = false;
            }
          });
        });
        setTiktokenSupportedModels(supportedModels);
      } catch (error) {
        console.error('Error fetching research services:', error);
        setJobCreationError('Failed to load research services. Please try again later.');
        setShowError(true);
      } finally {
        setLoadingServices(false);
      }
    };

    fetchServices();
  }, []);

  // Debounced token counter
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const debouncedTokenCounter = useCallback(
    debounce((text: string, model: string) => {
      if (!text || !model) {
        setTokenCount(0);
        setTokenCountError(null);
        return;
      }

      let enc: Tiktoken | null = null;
      try {
        enc = encoding_for_model(model as TiktokenModel);
        const tokens = enc.encode(text);
        setTokenCount(tokens.length);
        setTokenCountError(null);
      } catch (error) {
        // If model not supported by tiktoken, use a rough estimate
        setTokenCount(Math.ceil(text.length / 4));
        setTokenCountError('Token count is an estimate. This model is not fully supported by the token counter.');
      } finally {
        if (enc) {
          enc.free();
        }
      }
    }, 500), // 500ms debounce
    []
  );

  // Count tokens when prompt changes or model changes
  useEffect(() => {
    debouncedTokenCounter(prompt, selectedModel);
    
    // Cleanup function to cancel debounced calls
    return () => {
      debouncedTokenCounter.cancel();
    };
  }, [prompt, selectedModel, debouncedTokenCounter]);

  // Update max tokens when model changes
  useEffect(() => {
    if (!selectedModel || !selectedService) return;
    
    const service = services.find(s => s.service_key === selectedService);
    if (!service) return;
    
    const serviceModel = service.service_models.find(sm => sm.model.model_key === selectedModel);
    if (serviceModel) {
      setMaxTokens(serviceModel.model.max_tokens);
      
      // Initialize model params from default params
      const defaultParams = serviceModel.model.default_params;
      if (defaultParams && Object.keys(defaultParams).length > 0) {
        const initialParams = Object.entries(defaultParams).map(([key, value]) => ({
          key,
          value: String(value)
        }));
        setModelParams(initialParams);
      } else {
        setModelParams([{ key: '', value: '' }]);
      }
    }
  }, [selectedModel, selectedService, services]);

  // Handle service selection
  const handleServiceChange = (event: SelectChangeEvent) => {
    const serviceKey = event.target.value;
    setSelectedService(serviceKey);
    setSelectedModel(''); // Reset model when service changes
    setTokenCountError(null); // Clear any token count errors
  };

  // Handle model selection
  const handleModelChange = (event: SelectChangeEvent) => {
    const modelKey = event.target.value;
    setSelectedModel(modelKey);
    setTokenCountError(null); // Clear any token count errors
  };

  // Handle adding a new model parameter
  const handleAddParam = () => {
    setModelParams([...modelParams, { key: '', value: '' }]);
  };

  // Handle removing a model parameter
  const handleRemoveParam = (index: number) => {
    const updatedParams = [...modelParams];
    updatedParams.splice(index, 1);
    setModelParams(updatedParams);
  };

  // Handle changing a model parameter
  const handleParamChange = (index: number, field: 'key' | 'value', value: string) => {
    const updatedParams = [...modelParams];
    updatedParams[index][field] = value;
    setModelParams(updatedParams);
  };

  // Clean up polling interval when component unmounts
  useEffect(() => {
    return () => {
      if (pollInterval) {
        console.log('Component unmounting, clearing polling interval');
        clearInterval(pollInterval);
      }
    };
  }, [pollInterval]);

  // Handle error snackbar close
  const handleCloseError = () => {
    setShowError(false);
  };

  // Handle answer change for follow-up questions
  const handleAnswerChange = (index: number, value: string) => {
    const newAnswers = [...answers];
    newAnswers[index] = value;
    setAnswers(newAnswers);
  };

  // Handle submission of answers to follow-up questions
  const handleAnswerSubmit = async () => {
    if (!createdJob) return;
    
    try {
      setLoading(true);
      
      const result = await researchJobsApi.answerResearchJob({
        service: createdJob.service,
        job_id: createdJob.job_id,
        answers: answers
      });
      
      // Update job with the latest data
      setCreatedJob(result);
      
      // Reset question/answer state
      setQuestions([]);
      setAnswers([]);
      setIsAnswering(false);
      
      // Start polling for job status
      startPolling(result);
    } catch (error) {
      console.error('Error submitting answers:', error);
      // Handle error similar to job creation error
      let errorMessage = 'Failed to submit answers. Please try again later.';
      if (error instanceof Error) {
        errorMessage = `Error: ${error.message}`;
      }
      setJobCreationError(errorMessage);
      setShowError(true);
    } finally {
      setLoading(false);
    }
  };

  // Start polling for job status
  const startPolling = (job: ResearchJob) => {
    // Prevent creating multiple polling intervals
    if (isPollActive && pollInterval) {
      console.log('Polling already active, stopping previous polling before starting a new one');
      stopPolling();
    }
    
    console.log('Starting polling for job status');
    setIsPollActive(true);
    
    const interval = setInterval(async () => {
      try {
        console.log('Polling job status...');
        const updatedJob = await researchJobsApi.getResearchJob({
          job_id: job.job_id,
          service: job.service
        });
        
        setCreatedJob(updatedJob);
        
        // Check if job is complete, failed, or cancelled
        if (['completed', 'failed', 'cancelled'].includes(updatedJob.status)) {
          console.log(`Job status is ${updatedJob.status}, stopping polling`);
          stopPolling();
        }
      } catch (error) {
        console.error('Error polling job status:', error);
        stopPolling();
        // Handle error
        let errorMessage = 'Failed to get job status. Please check your research jobs page.';
        if (error instanceof Error) {
          errorMessage = `Error: ${error.message}`;
        }
        setJobCreationError(errorMessage);
        setShowError(true);
      }
    }, 5000); // Poll every 5 seconds
    
    setPollInterval(interval);
  };

  // Stop polling for job status
  const stopPolling = () => {
    console.log('Stopping polling');
    if (pollInterval) {
      clearInterval(pollInterval);
      console.log('Polling interval cleared');
    }
    setIsPollActive(false);
    setPollInterval(null);
    
    // Make sure loading state is also reset
    setLoading(false);
  };

  // Get color for status chip
  const getStatusColor = (status: ResearchJobStatus): "default" | "primary" | "secondary" | "error" | "info" | "success" | "warning" => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'cancelled':
        return 'error';
      case 'running':
        return 'primary';
      case 'pending_answers':
        return 'warning';
      default:
        return 'default';
    }
  };

  // Handle form submission
  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!selectedService || !selectedModel || !prompt) {
      return; // Basic validation
    }

    // Clear any previous errors
    setJobCreationError(null);

    try {
      setLoading(true);
      
      // Convert model params from array to object
      const paramsObject: Record<string, any> = {};
      modelParams.forEach(param => {
        if (param.key.trim()) {
          // Try to parse as number or boolean if possible
          const value = param.value.trim();
          let parsedValue: any = value;
          
          if (!isNaN(Number(value))) {
            parsedValue = Number(value);
          } else if (value.toLowerCase() === 'true') {
            parsedValue = true;
          } else if (value.toLowerCase() === 'false') {
            parsedValue = false;
          } else if (value.toLowerCase() === 'null') {
            parsedValue = null;
          } else {
            try {
              parsedValue = JSON.parse(value);
            } catch (error) {
              parsedValue = value;
            }
          }
          
          paramsObject[param.key.trim()] = parsedValue;
        }
      });
      
      // Create the job
      const result: ResearchJobCreateResponse = await researchJobsApi.createResearchJob({
        service: selectedService,
        model: selectedModel,
        prompt: prompt,
        model_params: Object.keys(paramsObject).length > 0 ? paramsObject : undefined
      });
      
      // Handle the response
      if (result.questions && result.questions.length > 0) {
        // Store the questions and set up for collecting answers
        setQuestions(result.questions);
        setAnswers(Array(result.questions.length).fill(''));
        setCreatedJob(result.job);
        setIsAnswering(true);
      } else {
        // No questions, proceed directly to polling
        setCreatedJob(result.job);
        startPolling(result.job);
      }
    } catch (error) {
      console.error('Error creating research job:', error);
      
      // Set a user-friendly error message
      let errorMessage = 'Failed to create research job. Please try again later.';
      if (error instanceof Error) {
        errorMessage = `Error: ${error.message}`;
      }
      
      setJobCreationError(errorMessage);
      setShowError(true);
    } finally {
      setLoading(false);
    }
  };

  // Get available models for the selected service
  const getAvailableModels = (): AiModel[] => {
    if (!selectedService) return [];
    
    const service = services.find(s => s.service_key === selectedService);
    if (!service) return [];
    
    return service.service_models.map(sm => sm.model);
  };

  // Check if a model is supported by tiktoken
  const isModelSupportedByTiktoken = (modelKey: string): boolean => {
    return !!tiktokenSupportedModels[modelKey];
  };

  // Calculate token usage percentage
  const tokenPercentage = maxTokens > 0 ? (tokenCount / maxTokens) * 100 : 0;
  const isTokenLimitExceeded = tokenPercentage > 90;

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Header subtitle="Create Research Job" />

      <NavBar />

      <Container component="main" sx={{ flexGrow: 1, py: 4 }}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h5" component="h1" gutterBottom>
            Create New Research Job
          </Typography>
          
          {/* Error message display */}
          <Snackbar 
            open={showError} 
            autoHideDuration={6000} 
            onClose={handleCloseError}
            anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
          >
            <Alert onClose={handleCloseError} severity="error" sx={{ width: '100%' }}>
              {jobCreationError}
            </Alert>
          </Snackbar>
          
          <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 3 }}>
            <Grid2 container spacing={3}>
              {/* Service Selection */}
              <Grid2 size={{ xs: 12, md: 6 }}>
                <FormControl fullWidth disabled={loadingServices || isAnswering || isPollActive}>
                  <InputLabel id="service-select-label">Research Service</InputLabel>
                  <Select
                    labelId="service-select-label"
                    id="service-select"
                    value={selectedService}
                    label="Research Service"
                    onChange={handleServiceChange}
                    required
                  >
                    {services.map((service) => (
                      <MenuItem key={service.id} value={service.service_key}>
                        {service.name}
                      </MenuItem>
                    ))}
                  </Select>
                  <FormHelperText>Select a research service</FormHelperText>
                </FormControl>
              </Grid2>

              {/* Model Selection */}
              <Grid2 size={{ xs: 12, md: 6 }}>
                <FormControl fullWidth disabled={!selectedService || isAnswering || isPollActive}>
                  <InputLabel id="model-select-label">Model</InputLabel>
                  <Select
                    labelId="model-select-label"
                    id="model-select"
                    value={selectedModel}
                    label="Model"
                    onChange={handleModelChange}
                    required
                  >
                    {getAvailableModels().map((model) => (
                      <MenuItem 
                        key={model.id} 
                        value={model.model_key}
                        disabled={!isModelSupportedByTiktoken(model.model_key)}
                      >
                        {model.model_key}
                      </MenuItem>
                    ))}
                  </Select>
                  <FormHelperText>
                    Select a model for this service
                    {selectedModel && !isModelSupportedByTiktoken(selectedModel) && 
                      " (Warning: Token counting may be inaccurate for this model)"}
                  </FormHelperText>
                </FormControl>
              </Grid2>

              {/* Model Parameters - only shown when not answering questions or polling */}
              {!isAnswering && !isPollActive && (
                <Grid2 size={{ xs: 12 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Model Parameters
                  </Typography>
                  
                  {modelParams.map((param, index) => (
                    <Grid2 container spacing={2} key={index} sx={{ mb: 2 }}>
                      <Grid2 size={{ xs: 5 }}>
                        <TextField
                          fullWidth
                          label="Parameter Name"
                          value={param.key}
                          onChange={(e) => handleParamChange(index, 'key', e.target.value)}
                          disabled={isAnswering || isPollActive}
                        />
                      </Grid2>
                      <Grid2 size={{ xs: 5 }}>
                        <TextField
                          fullWidth
                          label="Parameter Value"
                          value={param.value}
                          onChange={(e) => handleParamChange(index, 'value', e.target.value)}
                          disabled={isAnswering || isPollActive}
                        />
                      </Grid2>
                      <Grid2 size={{ xs: 2 }} sx={{ display: 'flex', alignItems: 'center' }}>
                        <IconButton 
                          color="error" 
                          onClick={() => handleRemoveParam(index)}
                          disabled={modelParams.length === 1 || isAnswering || isPollActive}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Grid2>
                    </Grid2>
                  ))}
                  
                  <Button
                    startIcon={<AddIcon />}
                    onClick={handleAddParam}
                    variant="outlined"
                    size="small"
                    sx={{ mt: 1 }}
                    disabled={isAnswering || isPollActive}
                  >
                    Add Parameter
                  </Button>
                </Grid2>
              )}

              {/* Prompt - disabled when answering or polling */}
              <Grid2 size={{ xs: 12 }}>
                <TextField
                  fullWidth
                  label="Research Prompt"
                  multiline
                  rows={6}
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  required
                  disabled={isAnswering || isPollActive}
                  error={isTokenLimitExceeded || !!tokenCountError}
                  helperText={
                    isTokenLimitExceeded
                      ? `Token count exceeds 90% of model's maximum (${tokenCount}/${maxTokens})`
                      : tokenCountError
                      ? `${tokenCountError} Current estimate: ${tokenCount}${maxTokens ? ` / ${maxTokens}` : ''}`
                      : `Token count: ${tokenCount}${maxTokens ? ` / ${maxTokens}` : ''}`
                  }
                />
              </Grid2>

              {/* Follow-up Questions section - only shown when isAnswering is true */}
              {isAnswering && questions.length > 0 && (
                <Grid2 size={{ xs: 12 }}>
                  <Divider sx={{ my: 4 }} />
                  <Typography variant="h5" sx={{ mb: 2 }}>
                    Follow-up Questions
                  </Typography>
                  
                  {questions.map((question, index) => (
                    <Box key={index} sx={{ mb: 3 }}>
                      <Typography variant="body1" sx={{ mb: 1, fontWeight: 'bold' }}>
                        {index + 1}. {question}
                      </Typography>
                      <TextField
                        fullWidth
                        multiline
                        rows={3}
                        value={answers[index] || ''}
                        onChange={(e) => handleAnswerChange(index, e.target.value)}
                        placeholder="Your answer"
                        variant="outlined"
                      />
                    </Box>
                  ))}
                  
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleAnswerSubmit}
                    disabled={answers.some(answer => !answer.trim()) || loading}
                    sx={{ mt: 2 }}
                  >
                    {loading ? <CircularProgress size={24} /> : 'Submit Answers'}
                  </Button>
                </Grid2>
              )}

              {/* Job Status section - only shown when createdJob is set and not answering questions */}
              {createdJob && !isAnswering && (
                <Grid2 size={{ xs: 12 }}>
                  <Divider sx={{ my: 4 }} />
                  <Typography variant="h5" sx={{ mb: 2 }}>
                    Research Job Status
                  </Typography>
                  
                  <Typography variant="body1" sx={{ mb: 1 }}>
                    Status: <Chip label={createdJob.status} color={getStatusColor(createdJob.status)} />
                  </Typography>
                  
                  {isPollActive && (
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 2, mb: 2 }}>
                      <CircularProgress size={24} sx={{ mr: 1 }} />
                      <Typography variant="body2">Updating status...</Typography>
                    </Box>
                  )}
                  
                  {createdJob.status === 'completed' && createdJob.deep_research_id && (
                    <Button
                      variant="contained"
                      color="primary"
                      component={Link}
                      to={`/research/${createdJob.deep_research_id}`}
                      sx={{ mt: 3 }}
                    >
                      View Results
                    </Button>
                  )}
                </Grid2>
              )}

              {/* Submit button - only shown when not answering or polling and no completed job exists */}
              {!isAnswering && !isPollActive && createdJob?.status !== 'completed' && (
                <Grid2 size={{ xs: 12 }}>
                  <Button
                    type="submit"
                    variant="contained"
                    color="primary"
                    size="large"
                    disabled={
                      loading || 
                      !selectedService || 
                      !selectedModel || 
                      !prompt || 
                      isTokenLimitExceeded
                    }
                    sx={{ mt: 2 }}
                  >
                    {loading ? <CircularProgress size={24} /> : 'Create Research Job'}
                  </Button>
                </Grid2>
              )}
            </Grid2>
          </Box>
        </Paper>
      </Container>

      <Footer />
    </div>
  );
};

export default CreateResearchJobPage; 