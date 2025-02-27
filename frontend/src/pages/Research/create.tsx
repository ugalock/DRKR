import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Alert,
  Box,
  Button,
  Container,
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
import NavBar from '../../components/common/NavBar';
import Footer from '../../components/common/Footer';
import { useApi } from '../../hooks/useApi';
import { ResearchService, AiModel } from '../../types/research_service';
import { encoding_for_model, type TiktokenModel, type Tiktoken } from 'tiktoken';
import debounce from 'lodash/debounce';

interface ModelParam {
  key: string;
  value: string;
}

const CreateResearchJobPage: React.FC = () => {
  const navigate = useNavigate();
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
  }, [researchServicesApi]);

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

  // Handle error snackbar close
  const handleCloseError = () => {
    setShowError(false);
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
          }
          
          paramsObject[param.key.trim()] = parsedValue;
        }
      });
      
      // Create the job
      const result = await researchJobsApi.createResearchJob({
        service: selectedService,
        model: selectedModel,
        prompt: prompt,
        model_params: Object.keys(paramsObject).length > 0 ? paramsObject : undefined
      });
      
      // TODO: Display follow up questions (if any), collect answers and send them to the backend, and then poll the backend for the status of the job until it's complete/failed/cancelled, displaying the results
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
      <header style={{ padding: '1rem', borderBottom: '1px solid #ccc' }}>
        <Typography variant="h4">DRKR</Typography>
        <Typography variant="h6">Create Research Job</Typography>
      </header>

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
                <FormControl fullWidth disabled={loadingServices}>
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
                <FormControl fullWidth disabled={!selectedService}>
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

              {/* Model Parameters */}
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
                      />
                    </Grid2>
                    <Grid2 size={{ xs: 5 }}>
                      <TextField
                        fullWidth
                        label="Parameter Value"
                        value={param.value}
                        onChange={(e) => handleParamChange(index, 'value', e.target.value)}
                      />
                    </Grid2>
                    <Grid2 size={{ xs: 2 }} sx={{ display: 'flex', alignItems: 'center' }}>
                      <IconButton 
                        color="error" 
                        onClick={() => handleRemoveParam(index)}
                        disabled={modelParams.length === 1}
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
                >
                  Add Parameter
                </Button>
              </Grid2>

              {/* Prompt */}
              <Grid2 size={{ xs: 12 }}>
                <TextField
                  fullWidth
                  label="Research Prompt"
                  multiline
                  rows={6}
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  required
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

              {/* Submit */}
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
            </Grid2>
          </Box>
        </Paper>
      </Container>

      <Footer />
    </div>
  );
};

export default CreateResearchJobPage; 