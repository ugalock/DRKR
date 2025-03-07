import React, { useEffect, useState, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Button,
  Chip,
  Container,
  Divider,
  Paper,
  Typography,
  Alert,
  AlertTitle,
  CircularProgress,
  Grid2,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Menu,
  MenuItem,
  ListItemText,
  Link,
  List,
  ListItem,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import ArrowRightIcon from '@mui/icons-material/ArrowRight';
import LinkIcon from '@mui/icons-material/Link';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import rehypeSanitize from 'rehype-sanitize';
import Header from '../../components/common/Header';
import NavBar from '../../components/common/NavBar';
import Footer from '../../components/common/Footer';
import { useApi } from '../../hooks/useApi';
import { DeepResearch } from '../../types/deep_research';
import { Tag } from '../../types/tag';
import { Organization } from '../../types/organization';
import { Visibility } from '../../types/research_job';
import { formatTimestamp } from '../../utils/formatters';
import VisibilityFilter from '../../components/VisibilityFilter';

// Interface for parsed Q&A pair
interface QuestionAnswer {
  question: string;
  answer: string;
}

const ResearchDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { deepResearchApi, organizationsApi } = useApi();
  
  const [research, setResearch] = useState<DeepResearch | null>(null);
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [questionAnswers, setQuestionAnswers] = useState<QuestionAnswer[]>([]);
  const [isMarkdown, setIsMarkdown] = useState<boolean>(false);
  // Add state for accordions
  const [jobExpanded, setJobExpanded] = useState<boolean>(false);
  const [questionsExpanded, setQuestionsExpanded] = useState<boolean>(false);
  const [reportExpanded, setReportExpanded] = useState<boolean>(false);
  const [sourcesExpanded, setSourcesExpanded] = useState<boolean>(false);  
  // Report view selection
  const [selectedReportView, setSelectedReportView] = useState<string>("full");
  const [reportViewAnchorEl, setReportViewAnchorEl] = useState<null | HTMLElement>(null);
  const [summariesAnchorEl, setSummariesAnchorEl] = useState<null | HTMLElement>(null);
  // Visibility state
  const [visibility, setVisibility] = useState<Visibility>('private');
  const [selectedOrgId, setSelectedOrgId] = useState<number | undefined>(undefined);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [orgNameMap, setOrgNameMap] = useState<Record<number, string>>({});
  const [loadingOrganizations, setLoadingOrganizations] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  
  // Create a mapping for summary lengths to user-friendly names
  const summaryNameMap: Record<string, string> = {
    "veryshort": "Quick read",
    "short": "Brief summary",
    "medium": "Standard summary",
    "long": "Detailed overview",
    "verylong": "In-depth overview"
  };

  // Get report summaries
  const reportSummaries = useMemo(() => {
    return research?.summaries?.filter(summary => 
      summary.summary_scope === 'report'
    ) || [];
  }, [research?.summaries]);

  // Parse questions and answers from text
  const parseQuestionsAndAnswers = (text: string | null) => {
    if (!text) return [];
    
    // Match Q: and A: patterns
    const regex = /Q:\s*(.*?)\s*\n\s*A:\s*(.*?)(?=\n\s*Q:|$)/gs;
    const matches: QuestionAnswer[] = [];
    
    let match;
    while ((match = regex.exec(text)) !== null) {
      matches.push({
        question: match[1].trim(),
        answer: match[2].trim()
      });
    }
    
    return matches;
  };

  // Check if text appears to be markdown
  const checkIfMarkdown = (text: string) => {
    // Simple heuristic: check for common markdown patterns
    const markdownPatterns = [
      /^#\s+.+$/m,             // Headers
      /\*\*.+\*\*/,             // Bold
      /\*.+\*/,                 // Italic
      /\[.+\]\(.+\)/,           // Links
      /!\[.+\]\(.+\)/,          // Images
      /^\s*-\s+.+$/m,           // Unordered lists
      /^\s*\d+\.\s+.+$/m,       // Ordered lists
      /```[\s\S]*?```/,         // Code blocks
      /`[^`]+`/,                // Inline code
      /^\s*>\s+.+$/m            // Blockquotes
    ];

    return markdownPatterns.some(pattern => pattern.test(text));
  };

  useEffect(() => {
    const fetchResearchData = async () => {
      if (!id) return;
      
      try {
        setLoading(true);
        const researchData = await deepResearchApi.getResearchById(id);
        setResearch(researchData);
        
        // Fetch tags for this research
        const tagsData = await deepResearchApi.getResearchTags(id);
        setTags(tagsData);
        
        // Parse questions and answers
        if (researchData.questions_and_answers) {
          setQuestionAnswers(parseQuestionsAndAnswers(researchData.questions_and_answers));
        }
        
        // Check if final report is markdown
        if (researchData.final_report) {
          setIsMarkdown(checkIfMarkdown(researchData.final_report));
        }
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching research data:', err);
        setError('Failed to load research data. Please try again later.');
        setLoading(false);
      }
    };

    fetchResearchData();
  }, [id]); // Remove deepResearchApi to prevent infinite loop

  // Fetch organizations
  useEffect(() => {
    const fetchOrganizations = async () => {
      try {
        setLoadingOrganizations(true);
        const organizations = await organizationsApi.getOrganizations();
        setOrganizations(organizations);
        
        // Create organization name lookup map
        const lookup = organizations.reduce((acc, org) => {
          if (org.id !== undefined) {
            acc[org.id] = org.name;
          }
          return acc;
        }, {} as Record<number, string>);
        setOrgNameMap(lookup);
      } catch (error) {
        console.error('Error fetching organizations:', error);
      } finally {
        setLoadingOrganizations(false);
      }
    };
    
    fetchOrganizations();
  }, []);

  // Set initial visibility state when research data is loaded
  useEffect(() => {
    if (research) {
      setVisibility(research.visibility || 'private');
      setSelectedOrgId(research.owner_org_id ? Number(research.owner_org_id) : undefined);
    }
  }, [research]);

  // Handle visibility change
  const handleVisibilityChange = (value: string, orgId?: number) => {
    setVisibility(value as Visibility);
    if (value !== 'org') {
      setSelectedOrgId(undefined);
    } else {
      setSelectedOrgId(orgId);
    }
  };

  // Check if visibility has changed from original
  const hasVisibilityChanged = (): boolean => {
    if (!research) return false;
    
    if (visibility !== research.visibility) return true;
    if (visibility === 'org') {
      // For org visibility, also check if org_id changed
      const researchOrgId = research.owner_org_id ? Number(research.owner_org_id) : undefined;
      return selectedOrgId !== researchOrgId;
    }
    return false;
  };

  // Handle saving visibility changes
  const handleSaveVisibilityChanges = async () => {
    if (!research || !hasVisibilityChanged()) return;
    
    try {
      setIsSaving(true);
      setSaveError(null);
      
      const updatedResearch = await deepResearchApi.updateResearch(research.id, {
        visibility: visibility,
        owner_org_id: visibility === 'org' ? selectedOrgId : undefined
      });
      
      // Update the research object with new values
      setResearch(updatedResearch);
    } catch (error) {
      console.error('Error updating research visibility:', error);
      setSaveError('Failed to update visibility. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  // Toggle accordion handlers
  const handleJobToggle = () => {
    setJobExpanded(!jobExpanded);
  };

  const handleQuestionsToggle = () => {
    setQuestionsExpanded(!questionsExpanded);
  };

  const handleReportToggle = () => {
    setReportExpanded(!reportExpanded);
  };

  const handleSourcesToggle = () => {
    setSourcesExpanded(!sourcesExpanded);
  };

  // Report menu handling
  const handleReportMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setReportViewAnchorEl(event.currentTarget);
  };

  const handleReportMenuClose = () => {
    setReportViewAnchorEl(null);
    setSummariesAnchorEl(null);
  };

  const handleSummariesMenuEnter = (event: React.MouseEvent<HTMLElement>) => {
    setSummariesAnchorEl(event.currentTarget);
  };

  const handleSummariesMenuLeave = () => {
    // Keep this empty - we'll handle closing in a different way
  };

  const handleViewSelect = (viewValue: string) => {
    setSelectedReportView(viewValue);
    handleReportMenuClose();
  };

  // Get displayed content based on selected view
  const getReportContent = () => {
    if (selectedReportView === "full") {
      return research?.final_report || "";
    }
    
    const selectedSummary = reportSummaries.find(
      summary => summary.summary_length === selectedReportView
    );
    
    return selectedSummary ? selectedSummary.summary_text : research?.final_report || "";
  };

  // Get current view display name
  const getCurrentViewName = (): string => {
    if (selectedReportView === "full") {
      return "Full report";
    }
    
    return summaryNameMap[selectedReportView] || "Full report";
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Header subtitle="Research Details" />
        <NavBar />
        <Container component="main" sx={{ flexGrow: 1, py: 4, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <CircularProgress />
        </Container>
        <Footer />
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Header subtitle="Research Details" />
        <NavBar />
        <Container component="main" sx={{ flexGrow: 1, py: 4 }}>
          <Alert severity="error">
            <AlertTitle>Error</AlertTitle>
            {error}
          </Alert>
        </Container>
        <Footer />
      </div>
    );
  }

  if (!research) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Header subtitle="Research Details" />
        <NavBar />
        <Container component="main" sx={{ flexGrow: 1, py: 4 }}>
          <Alert severity="warning">
            <AlertTitle>Not Found</AlertTitle>
            The requested research item could not be found.
          </Alert>
        </Container>
        <Footer />
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header subtitle="Research Details" />
      <NavBar />
      <Container component="main" sx={{ flexGrow: 1, py: 4 }}>
        <Paper sx={{ p: 3 }}>
          <Box sx={{ mb: 3 }}>
            <Typography variant="h4" gutterBottom>
              {research.title}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              {tags.map((tag) => (
                <Chip key={tag.id} label={tag.name} color="primary" variant="outlined" />
              ))}
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="subtitle1" color="text.secondary">
                Created: {formatTimestamp(research.created_at)}
                {research.created_at !== research.updated_at && 
                  ` | Updated: ${formatTimestamp(research.updated_at)}`}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {selectedOrgId && visibility === 'org' && organizations.length > 0 && (
                  <Box
                    component="span"
                    sx={{
                      px: 1,
                      py: 0.5,
                      borderRadius: 1,
                      typography: 'body2',
                      bgcolor: 'info.dark',
                      color: 'white',
                    }}
                  >
                    {orgNameMap[selectedOrgId] || 'Organization'}
                  </Box>
                )}
                <VisibilityFilter
                  value={visibility}
                  onChange={handleVisibilityChange}
                  organizations={organizations}
                  selectedOrgId={selectedOrgId}
                  showAllOption={false}
                  showAllOrganizationsOption={false}
                  loadingOrganizations={loadingOrganizations}
                />
              </Box>
            </Box>
            
            {/* Save Changes button - only shown when visibility has changed */}
            {hasVisibilityChanged() && (
              <Box sx={{ display: 'flex', justifyContent: 'flex-start', mt: 1, mb: 2 }}>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleSaveVisibilityChanges}
                  disabled={isSaving}
                  startIcon={isSaving ? <CircularProgress size={20} /> : null}
                >
                  {isSaving ? 'Saving...' : 'Save Changes'}
                </Button>
                {saveError && (
                  <Typography color="error" variant="body2" sx={{ ml: 2, alignSelf: 'center' }}>
                    {saveError}
                  </Typography>
                )}
              </Box>
            )}

            <Divider sx={{ my: 2 }} />
          </Box>

          <Grid2 container spacing={3}>
            <Grid2 size={{ xs: 12 }}>
              <Typography variant="h6" gutterBottom>
                Prompt
              </Typography>
              <Paper variant="outlined" sx={{ p: 2, backgroundColor: '#f8f9fa' }}>
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                  {research.prompt_text}
                </Typography>
              </Paper>
            </Grid2>

            <Grid2 size={{ xs: 12 }}>
              <Accordion 
                expanded={jobExpanded} 
                onChange={handleJobToggle}
                sx={{ mt: 3 }}
              >
                <AccordionSummary
                  expandIcon={jobExpanded ? <RemoveIcon /> : <AddIcon />}
                  aria-controls="research-job-content"
                  id="research-job-header"
                  sx={{ 
                    flexDirection: 'row-reverse',
                    '& .MuiAccordionSummary-expandIconWrapper': {
                      marginLeft: 0,
                      marginRight: 2  // Add margin to the right of the icon
                    }
                  }}
                >
                  <Typography variant="h6">
                    Research Job
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {research.research_job && (
                      <>
                        <Typography variant="body1">
                          <strong>Service:</strong> {research.research_job.service}
                        </Typography>
                        
                        <Box sx={{ display: 'flex', gap: 4 }}>
                          <Typography variant="body1">
                            <strong>Created:</strong> {formatTimestamp(research.research_job.created_at || research.created_at)}
                          </Typography>
                          {research.research_job.updated_at && research.research_job.created_at !== research.research_job.updated_at && (
                            <Typography variant="body1">
                              <strong>Updated:</strong> {formatTimestamp(research.research_job.updated_at)}
                            </Typography>
                          )}
                        </Box>
                      </>
                    )}
                    
                    {research.model_name && (
                      <Box sx={{ display: 'flex', flexDirection: 'row', gap: 4, alignItems: 'flex-start' }}>
                        <Typography variant="body1">
                          <strong>Model:</strong> {research.model_name}
                        </Typography>
                        
                        {research.model_params && (
                          <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                            <strong>Model Params:</strong> {typeof research.model_params === 'string' 
                              ? research.model_params 
                              : JSON.stringify(research.model_params, null)}
                          </Typography>
                        )}
                      </Box>
                    )}
                    
                    {research.model_name === undefined && research.model_params && (
                      <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                        <strong>Model Params:</strong> {typeof research.model_params === 'string' 
                          ? research.model_params 
                          : JSON.stringify(research.model_params, null)}
                      </Typography>
                    )}
                  </Box>
                </AccordionDetails>
              </Accordion>
            </Grid2>

            {questionAnswers.length > 0 && (
              <Grid2 size={{ xs: 12 }}>
                <Accordion 
                  expanded={questionsExpanded} 
                  onChange={handleQuestionsToggle}
                  sx={{ mt: 3 }}
                >
                  <AccordionSummary
                    expandIcon={questionsExpanded ? <RemoveIcon /> : <AddIcon />}
                    aria-controls="questions-answers-content"
                    id="questions-answers-header"
                    sx={{ 
                      flexDirection: 'row-reverse',
                      '& .MuiAccordionSummary-expandIconWrapper': {
                        marginLeft: 0,
                        marginRight: 2  // Add margin to the right of the icon
                      }
                    }}
                  >
                    <Typography variant="h6">
                      Clarifying Questions
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    {questionAnswers.map((qa, index) => (
                      <Paper 
                        key={index} 
                        variant="outlined" 
                        sx={{ p: 2, backgroundColor: '#f8f9fa', mb: 2 }}
                      >
                        <Typography 
                          variant="body1" 
                          sx={{ fontWeight: 'bold', mb: 1 }}
                        >
                          {qa.question}
                        </Typography>
                        <Typography variant="body1">
                          {qa.answer}
                        </Typography>
                      </Paper>
                    ))}
                  </AccordionDetails>
                </Accordion>
              </Grid2>
            )}

            <Grid2 size={{ xs: 12 }}>
              <Accordion 
                expanded={reportExpanded} 
                onChange={handleReportToggle}
                sx={{ mt: 3 }}
              >
                <AccordionSummary
                  expandIcon={reportExpanded ? <RemoveIcon /> : <AddIcon />}
                  aria-controls="final-report-content"
                  id="final-report-header"
                  sx={{ 
                    flexDirection: 'row-reverse',
                    '& .MuiAccordionSummary-expandIconWrapper': {
                      marginLeft: 0,
                      marginRight: 2  // Add margin to the right of the icon
                    }
                  }}
                >
                  <Typography variant="h6">
                    Report
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  {/* Report selection UI */}
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Box>
                      <Button
                        variant="outlined"
                        size="small"
                        endIcon={<ArrowDropDownIcon />}
                        onClick={handleReportMenuOpen}
                        aria-controls="report-menu"
                        aria-haspopup="true"
                      >
                        {getCurrentViewName()}
                      </Button>
                      
                      {/* Main dropdown menu */}
                      <Menu
                        id="report-menu"
                        anchorEl={reportViewAnchorEl}
                        open={Boolean(reportViewAnchorEl)}
                        onClose={handleReportMenuClose}
                        MenuListProps={{
                          'aria-labelledby': 'report-view-button',
                        }}
                      >
                        <MenuItem 
                          onClick={() => handleViewSelect('full')}
                          selected={selectedReportView === 'full'}
                        >
                          <ListItemText>Full report</ListItemText>
                        </MenuItem>
                        
                        {reportSummaries.length > 0 && (
                          <MenuItem 
                            onMouseEnter={handleSummariesMenuEnter}
                            onMouseLeave={handleSummariesMenuLeave}
                          >
                            <ListItemText>Summaries</ListItemText>
                            <ArrowRightIcon fontSize="small" />
                          </MenuItem>
                        )}
                      </Menu>
                      
                      {/* Submenu for summaries */}
                      <Menu
                        id="summaries-menu"
                        anchorEl={summariesAnchorEl}
                        open={Boolean(summariesAnchorEl)}
                        onClose={handleReportMenuClose}
                        anchorOrigin={{
                          vertical: 'top',
                          horizontal: 'right',
                        }}
                        transformOrigin={{
                          vertical: 'top',
                          horizontal: 'left',
                        }}
                        MenuListProps={{
                          onMouseLeave: handleReportMenuClose
                        }}
                      >
                        {reportSummaries.map((summary) => (
                          <MenuItem 
                            key={summary.id}
                            onClick={() => handleViewSelect(summary.summary_length)}
                            selected={selectedReportView === summary.summary_length}
                          >
                            <ListItemText>
                              {summaryNameMap[summary.summary_length] || summary.summary_length}
                            </ListItemText>
                          </MenuItem>
                        ))}
                      </Menu>
                    </Box>
                  </Box>
                  
                  {/* Display selected report content */}
                  <Paper variant="outlined" sx={{ p: 2, backgroundColor: '#f8f9fa' }}>
                    {isMarkdown ? (
                      <Box sx={{ 
                        '& a': { color: 'primary.main' },
                        '& h1': { 
                          fontSize: '2rem',
                          fontWeight: 'bold',
                          marginTop: '1.5rem',
                          marginBottom: '1rem',
                          borderBottom: '1px solid #eaecef',
                          paddingBottom: '0.3rem'
                        },
                        '& h2': { 
                          fontSize: '1.5rem',
                          fontWeight: 'bold',
                          marginTop: '1.5rem',
                          marginBottom: '0.75rem',
                          borderBottom: '1px solid #eaecef',
                          paddingBottom: '0.3rem'
                        },
                        '& h3': { 
                          fontSize: '1.25rem',
                          fontWeight: 'bold',
                          marginTop: '1.25rem',
                          marginBottom: '0.5rem' 
                        },
                        '& h4': { 
                          fontSize: '1rem',
                          fontWeight: 'bold',
                          marginTop: '1rem',
                          marginBottom: '0.5rem' 
                        },
                        '& h5': { 
                          fontSize: '0.875rem',
                          fontWeight: 'bold',
                          marginTop: '0.875rem',
                          marginBottom: '0.5rem' 
                        },
                        '& h6': { 
                          fontSize: '0.85rem',
                          fontWeight: 'bold',
                          color: 'text.secondary',
                          marginTop: '0.85rem',
                          marginBottom: '0.5rem' 
                        },
                        '& p': {
                          marginTop: '0.5rem',
                          marginBottom: '1rem',
                          lineHeight: 1.6
                        },
                        '& ul, & ol': {
                          paddingLeft: '2rem',
                          marginBottom: '1rem'
                        },
                        '& li': {
                          marginBottom: '0.5rem'
                        },
                        '& li > ul, & li > ol': {
                          marginTop: '0.5rem',
                          marginBottom: '0.5rem'
                        },
                        '& ul ul, & ol ol, & ul ol, & ol ul': {
                          marginBottom: 0
                        },
                        '& ul': {
                          listStyleType: 'disc'
                        },
                        '& ul ul': {
                          listStyleType: 'circle'
                        },
                        '& ul ul ul': {
                          listStyleType: 'square'
                        },
                        '& ol': {
                          listStyleType: 'decimal'
                        },
                        '& ol ol': {
                          listStyleType: 'lower-alpha'
                        },
                        '& ol ol ol': {
                          listStyleType: 'lower-roman'
                        },
                        '& code': { 
                          backgroundColor: 'rgba(0, 0, 0, 0.05)', 
                          padding: '0.2em 0.4em',
                          borderRadius: '3px',
                          fontFamily: 'monospace',
                          fontSize: '85%'
                        },
                        '& pre': {
                          backgroundColor: 'rgba(0, 0, 0, 0.05)', 
                          padding: '1em',
                          borderRadius: '4px',
                          overflow: 'auto',
                          marginBottom: '1rem'
                        },
                        '& pre code': {
                          background: 'none',
                          padding: 0
                        },
                        '& blockquote': {
                          borderLeft: '4px solid #ccc',
                          paddingLeft: '1em',
                          margin: '1em 0',
                          color: 'text.secondary'
                        },
                        '& hr': {
                          height: '0.25em',
                          padding: 0,
                          margin: '24px 0',
                          backgroundColor: '#e1e4e8',
                          border: 0
                        },
                        '& table': {
                          borderCollapse: 'collapse',
                          width: '100%',
                          marginBottom: '1rem'
                        },
                        '& th, & td': {
                          border: '1px solid #ddd',
                          padding: '8px',
                          textAlign: 'left'
                        },
                        '& th': {
                          backgroundColor: 'rgba(0, 0, 0, 0.04)',
                          fontWeight: 'bold'
                        },
                        '& img': {
                          maxWidth: '100%',
                          margin: '1rem 0'
                        },
                        '& strong': {
                          fontWeight: 'bold'
                        },
                        '& em': {
                          fontStyle: 'italic'
                        }
                      }}>
                        <ReactMarkdown 
                          remarkPlugins={[remarkGfm]} 
                          rehypePlugins={[rehypeRaw, rehypeSanitize]}
                        >
                          {getReportContent()}
                        </ReactMarkdown>
                      </Box>
                    ) : (
                      <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                        {getReportContent()}
                      </Typography>
                    )}
                  </Paper>
                </AccordionDetails>
              </Accordion>
            </Grid2>

            {/* Sources section - only show if sources exist */}
            {research?.sources && research.sources.length > 0 && (
              <Grid2 size={{ xs: 12 }}>
                <Accordion 
                  expanded={sourcesExpanded} 
                  onChange={handleSourcesToggle}
                  sx={{ mt: 3 }}
                >
                  <AccordionSummary
                    expandIcon={sourcesExpanded ? <RemoveIcon /> : <AddIcon />}
                    aria-controls="sources-content"
                    id="sources-header"
                    sx={{ 
                      flexDirection: 'row-reverse',
                      '& .MuiAccordionSummary-expandIconWrapper': {
                        marginLeft: 0,
                        marginRight: 2
                      }
                    }}
                  >
                    <Typography variant="h6">
                      Sources ({research.sources.length})
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <List sx={{ width: '100%' }}>
                      {research.sources.map((source) => (
                        <ListItem key={source.id} sx={{ py: 1 }}>
                          <LinkIcon sx={{ mr: 1, color: 'primary.main' }} fontSize="small" />
                          <Link 
                            href={source.source_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            underline="hover"
                          >
                            {source.source_title || source.source_url}
                          </Link>
                          {source.domain && (
                            <Typography 
                              variant="body2" 
                              color="text.secondary" 
                              sx={{ ml: 1 }}
                            >
                              ({source.domain})
                            </Typography>
                          )}
                        </ListItem>
                      ))}
                    </List>
                  </AccordionDetails>
                </Accordion>
              </Grid2>
            )}
          </Grid2>
        </Paper>
      </Container>
      <Footer />
    </div>
  );
};

export default ResearchDetailPage; 