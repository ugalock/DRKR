import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
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
  Tooltip,
} from '@mui/material';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import RefreshIcon from '@mui/icons-material/Refresh';
import VisibilityFilter from '../../components/VisibilityFilter';
import Header from '../../components/common/Header';
import Footer from '../../components/common/Footer';
import NavBar from '../../components/common/NavBar';
import { ResearchJob } from '../../types/research_job';
import { Organization } from '../../types/organization';
import { User } from '../../types/user';
import { useApi } from '../../hooks/useApi';
import { formatTimestamp } from '../../utils/formatters';

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
  { id: 'visibility', label: 'Visibility', sortable: false, filterable: true },
  { id: 'status', label: 'Status', sortable: true, filterable: true },
  { id: 'created_at', label: 'Created', sortable: true, filterable: false },
  { id: 'updated_at', label: 'Last Updated', sortable: true, filterable: false },
];

interface RowProps {
  job: ResearchJob;
  orgName?: string;
  user_id?: number;
  onCancelJob: (jobId: number) => Promise<void>;
  onRefreshJob: (jobId: number) => Promise<void>;
}

const JobRow: React.FC<RowProps> = ({ job, orgName, user_id, onCancelJob, onRefreshJob }) => {
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

  const canBeCancelled = !['completed', 'failed', 'cancelled'].includes(job.status) && job.user_id === user_id;

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
          <Tooltip title={orgName || job.visibility}>
            <Box
              component="span"
              sx={{
                px: 1,
                py: 0.5,
                borderRadius: 1,
                typography: 'body2',
                maxWidth: '150px',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                display: 'inline-block',
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
              {orgName || job.visibility}
            </Box>
          </Tooltip>
        </TableCell>
        <TableCell>{job.status}</TableCell>
        <TableCell>{formatTimestamp(job.created_at!)}</TableCell>
        <TableCell>
          {formatTimestamp(job.updated_at!)}
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

// Define types based on the columns array
type SortableColumn = Extract<keyof ResearchJob, typeof columns[number]['id']> & {
  [K in typeof columns[number]['id']]: Extract<typeof columns[number], { id: K }>['sortable'] extends true ? K : never
}[typeof columns[number]['id']];

type FilterableColumn = Extract<keyof ResearchJob, typeof columns[number]['id']> & {
  [K in typeof columns[number]['id']]: Extract<typeof columns[number], { id: K }>['filterable'] extends true ? K : never
}[typeof columns[number]['id']];

const ResearchJobsPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { researchJobsApi, organizationsApi, userApi } = useApi();
  
  // Ref to track if we've already redirected
  const hasRedirectedRef = useRef(false);
  
  // For runtime reference, compute the actual column IDs
  const sortableColumnIds = columns
    .filter(column => column.sortable)
    .map(column => column.id);
  
  const filterableColumnIds = columns
    .filter(column => column.filterable)
    .map(column => column.id);
  
  // Parse and validate orderBy - check against actual sortable columns
  const queryOrderByParam = searchParams.get('orderBy') as string | null;
  const queryOrderBy: SortableColumn = queryOrderByParam && sortableColumnIds.includes(queryOrderByParam as keyof ResearchJob) 
    ? queryOrderByParam as SortableColumn
    : 'created_at';
  
  // Parse and validate order
  const queryOrderParam = searchParams.get('order');
  const queryOrder: Order = queryOrderParam === 'asc' || queryOrderParam === 'desc' 
    ? queryOrderParam 
    : 'desc';
  
  const queryOrgId = searchParams.get('orgId') ? Number(searchParams.get('orgId')) : undefined;
  
  // Initialize filter state
  const initialFilters: Partial<Record<FilterableColumn, string>> = {};
  
  // Filter parameters - only keep valid filterable columns
  Array.from(searchParams.entries()).forEach(([key, value]) => {
    if (filterableColumnIds.includes(key as keyof ResearchJob)) {
      initialFilters[key as FilterableColumn] = value;
    }
  });
  
  // If queryOrgId is present, ensure visibility is set to 'org'
  if (queryOrgId !== undefined) {
    initialFilters.visibility = 'org';
  }
  
  // State with more specific types
  const [jobs, setJobs] = useState<ResearchJob[]>([]);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [orgNameMap, setOrgNameMap] = useState<Record<number, string>>({});
  const [user, setUser] = useState<User | null>(null);
  const [initialLoading, setInitialLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(20);
  const [orderBy, setOrderBy] = useState<SortableColumn>(queryOrderBy);
  const [order, setOrder] = useState<Order>(queryOrder);
  const [filters, setFilters] = useState<Partial<Record<FilterableColumn, string>>>(initialFilters);
  const [selectedOrgId, setSelectedOrgId] = useState<number | undefined>(queryOrgId);
  const [organizationsLoaded, setOrganizationsLoaded] = useState(false);
  const isFetchingRef = useRef(false);
  
  // Redirect to clean URL if we came in with query params
  useEffect(() => {
    if (searchParams.toString() && !hasRedirectedRef.current) {
      hasRedirectedRef.current = true;
      navigate('/research/jobs', { replace: true });
    }
  }, [searchParams, navigate]);

  useEffect(() => {
    const fetchUser = async () => {
      const user = await userApi.getCurrentUser();
      setUser(user);
    };
    fetchUser();
  }, []);
  
  const fetchJobs = async () => {
    // Skip if already fetching
    if (isFetchingRef.current) return;
    
    try {
      isFetchingRef.current = true;
      // Only set refreshing state if we already have data
      if (!initialLoading) {
        setIsRefreshing(true);
      }
      
      const response = await researchJobsApi.getResearchJobs({
        page: page + 1,
        limit: rowsPerPage,
        visibility: filters.visibility as string,
        org_id: selectedOrgId,
        order_by: orderBy,
        order: order,
        ...Object.fromEntries(
          Object.entries(filters).filter(([key]) => key !== 'visibility')
        )
      });
      setJobs(response);
    } catch (error) {
      console.error('Error fetching jobs:', error);
    } finally {
      setInitialLoading(false);
      setIsRefreshing(false);
      isFetchingRef.current = false;
    }
  };

  // Only fetch jobs when organizations are loaded
  useEffect(() => {
    if (organizationsLoaded) {
      fetchJobs();
    }
  }, [page, rowsPerPage, filters, selectedOrgId, organizationsLoaded]);

  // Load organizations, validate selectedOrgId, and create lookup map
  useEffect(() => {
    const loadOrgs = async () => {
      try {
        const orgs = await organizationsApi.getOrganizations();
        setOrganizations(orgs);
        
        // Validate selectedOrgId if one is provided from query params
        if (selectedOrgId !== undefined) {
          const orgExists = orgs.some(org => org.id === selectedOrgId);
          if (!orgExists) {
            setSelectedOrgId(undefined);

            // If we're removing an invalid orgId, also clear the 'org' visibility filter
            if (filters.visibility === 'org') {
              setFilters(prev => {
                const newFilters = { ...prev };
                delete newFilters.visibility;
                return newFilters;
              });
            }
          } else if (filters.visibility !== 'org') {
            // Ensure visibility is 'org' if we have a valid selectedOrgId
            setFilters(prev => ({ ...prev, visibility: 'org' }));
          }
        }
        // Create organization name lookup map
        const lookup = orgs.reduce((acc, org) => {
          if (org.id !== undefined) {
            acc[org.id] = org.name;
          }
          return acc;
        }, {} as Record<number, string>);
        setOrgNameMap(lookup);
        
        setOrganizationsLoaded(true);
      } catch (error) {
        console.error('Error loading organizations:', error);
        setOrganizationsLoaded(true); // Still mark as loaded to avoid infinite loading
      }
    };
    loadOrgs();
  }, []);

  // Update handleSort to use the more specific type
  const handleSort = (property: SortableColumn) => {
    // No need to check if sortable - the type system ensures it
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

  // Update handleFilterChange to use the more specific type
  const handleFilterChange = (column: FilterableColumn) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    // No need to check if filterable - the type system ensures it
    const newValue = event.target.value;
    setFilters(prevFilters => {
      const newFilters = { ...prevFilters };
      if (newValue) {
        newFilters[column] = newValue;
      } else {
        delete newFilters[column];
      }
      return newFilters;
    });
    // setPage(0);
  };

  const updateJob = (updatedJob: ResearchJob) => {
    setJobs(currentJobs => 
      currentJobs.map(job => 
        job.job_id === updatedJob.job_id ? updatedJob : job
      )
    );
  };

  const handleCancelJob = async (id: number) => {
    try {
      const updatedJob = await researchJobsApi.updateResearchJob(id, {
        status: 'cancelled'
      });
      updateJob(updatedJob);
    } catch (error) {
      console.error('Error cancelling job:', error);
    }
  };

  const handleRefreshJob = async (id: number) => {
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
      const columnKey = key as FilterableColumn;
      const jobValue = job[columnKey];
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

  // Update handleVisibilityChange
  const handleVisibilityChange = (value: string, orgId?: number) => {
    setFilters(prev => {
      const newFilters = { ...prev };
      if (value) {
        newFilters.visibility = value;
      } else {
        delete newFilters.visibility;
      }
      return newFilters;
    });
    
    if (value !== 'org') {
      setSelectedOrgId(undefined);
    } else {
      setSelectedOrgId(orgId);
    }
    setPage(0);
  };

  if (initialLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Header subtitle="Research Jobs" />

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
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      <Box sx={{ height: '28px', display: 'flex', alignItems: 'center' }}>
                        {column.sortable ? (
                          <TableSortLabel
                            active={orderBy === column.id}
                            direction={orderBy === column.id ? order : 'asc'}
                            onClick={() => handleSort(column.id as SortableColumn)}
                          >
                            {column.label}
                          </TableSortLabel>
                        ) : (
                          <Typography
                            variant="inherit"
                            display="block"
                            style={{ fontWeight: 'inherit' }}
                          >
                            {column.label}
                          </Typography>
                        )}
                      </Box>
                      
                      {column.filterable && column.id === 'visibility' ? (
                        <VisibilityFilter
                          value={filters[column.id as FilterableColumn] || ''}
                          organizations={organizations}
                          selectedOrgId={selectedOrgId}
                          onChange={handleVisibilityChange}
                        />
                      ) : column.filterable ? (
                        <TextField
                          size="small"
                          placeholder={`Filter ${column.label}`}
                          value={filters[column.id as FilterableColumn] || ''}
                          onChange={handleFilterChange(column.id as FilterableColumn)}
                        />
                      ) : (
                        <Box sx={{ height: '40px' }} />
                      )}
                    </Box>
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody sx={{ opacity: isRefreshing ? 0.5 : 1, transition: 'opacity 0.2s' }}>
              {paginatedJobs.map((job) => (
                <JobRow 
                  key={job.job_id} 
                  job={job}
                  user_id={user?.id}
                  orgName={job.visibility === 'org' && job.owner_org_id ? 
                    orgNameMap[Number(job.owner_org_id)] : undefined}
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
