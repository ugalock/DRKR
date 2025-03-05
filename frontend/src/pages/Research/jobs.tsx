import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  IconButton,
  Collapse,
  Box,
  Typography,
  TablePagination,
  TableSortLabel,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import RefreshIcon from '@mui/icons-material/Refresh';
import Footer from '../../components/common/Footer';
import NavBar from '../../components/common/NavBar';
import { ResearchJob } from '../../types/research_job';
import { useApi } from '../../hooks/useApi';

type Order = 'asc' | 'desc';

interface Column {
  id: keyof ResearchJob;
  label: string;
  sortable: boolean;
  filterable: boolean;
}

const columns: Column[] = [
  { id: 'service', label: 'Service', sortable: true, filterable: true },
  { id: 'model_name', label: 'Model', sortable: true, filterable: true },
  { id: 'visibility', label: 'Visibility', sortable: true, filterable: true },
  { id: 'status', label: 'Status', sortable: true, filterable: true },
  { id: 'created_at', label: 'Created', sortable: true, filterable: false },
  { id: 'updated_at', label: 'Last Updated', sortable: true, filterable: false },
];

interface RowProps {
  job: ResearchJob;
  onCancelJob: (jobId: string) => Promise<void>;
  onRefreshJob: (jobId: string) => Promise<void>;
}

const JobRow: React.FC<RowProps> = ({ job, onCancelJob, onRefreshJob }) => {
  const [open, setOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleCancel = async () => {
    setIsLoading(true);
    try {
      await onCancelJob(job.id);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    setIsLoading(true);
    try {
      await onRefreshJob(job.id);
    } finally {
      setIsLoading(false);
    }
  };

  const canBeCancelled = !['completed', 'failed', 'cancelled'].includes(job.status);

  return (
    <>
      <TableRow sx={{ '& > *': { borderBottom: 'unset' } }}>
        <TableCell>
          <IconButton size="small" onClick={() => setOpen(!open)}>
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell>{job.service}</TableCell>
        <TableCell>{job.model_name}</TableCell>
        <TableCell>
          <Box
            component="span"
            sx={{
              px: 1,
              py: 0.5,
              borderRadius: 1,
              typography: 'body2',
              bgcolor: job.visibility === 'public' 
                ? 'success.light' 
                : job.visibility === 'org' 
                ? 'info.light' 
                : 'grey.200',
              color: job.visibility === 'public' 
                ? 'success.dark' 
                : job.visibility === 'org' 
                ? 'info.dark' 
                : 'grey.700',
            }}
          >
            {job.visibility}
          </Box>
        </TableCell>
        <TableCell>{job.status}</TableCell>
        <TableCell>{new Date(job.created_at!).toLocaleString()}</TableCell>
        <TableCell>
          {new Date(job.updated_at!).toLocaleString()}
          {canBeCancelled && (
            <IconButton 
              size="small" 
              onClick={handleRefresh}
              disabled={isLoading}
              sx={{ ml: 1 }}
            >
              <RefreshIcon fontSize="small" />
            </IconButton>
          )}
        </TableCell>
      </TableRow>
      <TableRow>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={7}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ margin: 1 }}>
              <Typography variant="h6" gutterBottom component="div">
                Job Details
              </Typography>
              <Typography>Job ID: {job.job_id}</Typography>
              {job.model_params && (
                <Typography>
                  Parameters: {JSON.stringify(job.model_params, null, 2)}
                </Typography>
              )}
              {canBeCancelled && (
                <Button
                  variant="contained"
                  color="secondary"
                  onClick={handleCancel}
                  disabled={isLoading}
                  sx={{ mt: 2 }}
                >
                  Cancel Job
                </Button>
              )}
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </>
  );
};

const ResearchJobsPage: React.FC = () => {
  const navigate = useNavigate();
  const { researchJobsApi } = useApi();
  const [jobs, setJobs] = useState<ResearchJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(20);
  const [orderBy, setOrderBy] = useState<keyof ResearchJob>('created_at');
  const [order, setOrder] = useState<Order>('desc');
  const [filters, setFilters] = useState<Partial<Record<keyof ResearchJob, string>>>({});
  const isFetchingRef = useRef(false);
  
  const fetchJobs = async () => {
    // Skip if already fetching
    if (isFetchingRef.current) return;
    
    try {
      isFetchingRef.current = true;
      setLoading(true);
      
      const response = await researchJobsApi.getResearchJobs({
        page: page + 1,
        limit: rowsPerPage,
      });
      setJobs(response);
    } catch (error) {
      console.error('Error fetching jobs:', error);
    } finally {
      setLoading(false);
      isFetchingRef.current = false;
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [page, rowsPerPage]);

  const handleSort = (property: keyof ResearchJob) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleFilterChange = (column: keyof ResearchJob) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFilters({ ...filters, [column]: event.target.value });
    // setPage(1);
  };

  const updateJob = (updatedJob: ResearchJob) => {
    setJobs(currentJobs => 
      currentJobs.map(job => 
        job.job_id === updatedJob.job_id ? updatedJob : job
      )
    );
  };

  const handleCancelJob = async (id: string) => {
    try {
      const updatedJob = await researchJobsApi.updateResearchJob(id, {
        status: 'cancelled'
      });
      updateJob(updatedJob);
    } catch (error) {
      console.error('Error cancelling job:', error);
    }
  };

  const handleRefreshJob = async (id: string) => {
    try {
      const updatedJob = await researchJobsApi.getResearchJob({
        id: id
      });
      updateJob(updatedJob);
    } catch (error) {
      console.error('Error refreshing job:', error);
    }
  };

  const filteredJobs = jobs.filter((job) => {
    return Object.entries(filters).every(([key, value]) => {
      if (!value) return true;
      const jobValue = job[key as keyof ResearchJob];
      return jobValue?.toString().toLowerCase().includes(value.toLowerCase());
    });
  });

  const sortedJobs = [...filteredJobs].sort((a, b) => {
    const aValue = a[orderBy];
    const bValue = b[orderBy];
    
    if (!aValue || !bValue) return 0;
    
    const comparison = aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
    return order === 'desc' ? -comparison : comparison;
  });

  const paginatedJobs = sortedJobs;

  // Custom filter component for visibility
  const VisibilityFilter: React.FC<{
    value: string;
    onChange: (value: string) => void;
  }> = ({ value, onChange }) => (
    <FormControl size="small" sx={{ mt: 1, minWidth: 120 }}>
      <InputLabel id="visibility-filter-label">Visibility</InputLabel>
      <Select
        labelId="visibility-filter-label"
        value={value}
        label="Visibility"
        onChange={(e) => onChange(e.target.value)}
      >
        <MenuItem value="">All</MenuItem>
        <MenuItem value="private">Private</MenuItem>
        <MenuItem value="public">Public</MenuItem>
        <MenuItem value="org">Organization</MenuItem>
      </Select>
    </FormControl>
  );

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{ padding: '1rem', borderBottom: '1px solid #ccc' }}>
        <Typography variant="h4">DRKR</Typography>
        <Typography variant="h6">Research Jobs</Typography>
      </header>

      <NavBar />

      <main style={{ flex: 1, padding: '2rem' }}>
        <Box sx={{ mb: 3 }}>
          <Button
            variant="contained"
            color="primary"
            onClick={() => navigate('/research/create-job')}
          >
            Create New Job
          </Button>
        </Box>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell /> {/* Expansion column */}
                {columns.map((column) => (
                  <TableCell key={column.id}>
                    <TableSortLabel
                      active={orderBy === column.id}
                      direction={orderBy === column.id ? order : 'asc'}
                      onClick={() => column.sortable && handleSort(column.id)}
                    >
                      {column.label}
                    </TableSortLabel>
                    {column.filterable && column.id === 'visibility' ? (
                      <VisibilityFilter
                        value={filters[column.id] || ''}
                        onChange={(value) => {
                          setFilters({ ...filters, [column.id]: value });
                          setPage(0);
                        }}
                      />
                    ) : column.filterable ? (
                      <TextField
                        size="small"
                        placeholder={`Filter ${column.label}`}
                        value={filters[column.id] || ''}
                        onChange={handleFilterChange(column.id)}
                        sx={{ mt: 1 }}
                      />
                    ) : null}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedJobs.map((job) => (
                <JobRow 
                  key={job.job_id} 
                  job={job} 
                  onCancelJob={handleCancelJob}
                  onRefreshJob={handleRefreshJob}
                />
              ))}
            </TableBody>
          </Table>
          <TablePagination
            component="div"
            count={filteredJobs.length}
            page={page}
            onPageChange={handleChangePage}
            rowsPerPage={rowsPerPage}
            rowsPerPageOptions={[10, 20, 50, 100]}
            onRowsPerPageChange={handleChangeRowsPerPage}
            disabled={isFetchingRef.current}
          />
        </TableContainer>
      </main>

      <Footer />
    </div>
  );
};

export default ResearchJobsPage;
