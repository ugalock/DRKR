import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Collapse,
  Box,
  Typography,
  TablePagination,
  TableSortLabel,
  TextField,
  Tooltip,
  Button,
} from '@mui/material';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import VisibilityFilter from '../../components/VisibilityFilter';
import Header from '../../components/common/Header';
import Footer from '../../components/common/Footer';
import NavBar from '../../components/common/NavBar';
import { DeepResearch } from '../../types/deep_research';
import { Organization } from '../../types/organization';
import { useApi } from '../../hooks/useApi';
import { formatTimestamp } from '../../utils/formatters';

type Order = 'asc' | 'desc';

interface Column {
  id: keyof DeepResearch;
  label: string;
  sortable: boolean;
  filterable: boolean;
}

const columns: Column[] = [
  { id: 'creator_username', label: 'Created By', sortable: true, filterable: true },
  { id: 'avg_rating', label: 'Rating', sortable: true, filterable: false },
  { id: 'model_name', label: 'Model', sortable: true, filterable: true },
  { id: 'visibility', label: 'Visibility', sortable: false, filterable: true },
  { id: 'created_at', label: 'Created', sortable: true, filterable: false },
  { id: 'updated_at', label: 'Last Updated', sortable: true, filterable: false },
];

interface RowProps {
  entry: DeepResearch;
  orgName?: string;
}

const EntryRow: React.FC<RowProps> = ({ entry, orgName }) => {
  const [open, setOpen] = useState(false);

  return (
    <>
      <TableRow sx={{ '& > *': { borderBottom: 'unset' } }}>
        <TableCell>
          <IconButton size="small" onClick={() => setOpen(!open)}>
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell>{entry.creator_username}</TableCell>
        <TableCell>
          {entry.ratings?.length ?? 0 > 0 
            ? `${entry.avg_rating?.toFixed(1) || '0.0'} / 5.0`
            : 'No ratings'}
        </TableCell>
        <TableCell>{entry.model_name}</TableCell>
        <TableCell>
          <Tooltip title={orgName || entry.visibility}>
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
                bgcolor: entry.visibility === 'public' 
                  ? 'success.light' 
                  : entry.visibility === 'org' 
                  ? 'info.light' 
                  : 'grey.200',
                color: entry.visibility === 'public' 
                  ? 'success.dark' 
                  : entry.visibility === 'org' 
                  ? 'info.dark' 
                  : 'grey.700',
              }}
            >
              {orgName || entry.visibility}
            </Box>
          </Tooltip>
        </TableCell>
        <TableCell>{formatTimestamp(entry.created_at!)}</TableCell>
        <TableCell>{formatTimestamp(entry.updated_at!)}</TableCell>
      </TableRow>
      <TableRow>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={7}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ margin: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>

                <Button 
                  variant="contained" 
                  color="primary" 
                  component={Link} 
                  to={`/research/${entry.id}`}
                  size="small"
                >
                  View Entry
                </Button>
              </Box>
              <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
                Prompt:
              </Typography>
              <Typography sx={{ mb: 2, whiteSpace: 'pre-wrap' }}>
                {entry.prompt_text}
              </Typography>
              {entry.model_params && (
                <>
                  <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
                    Model Parameters:
                  </Typography>
                  <Typography sx={{ mb: 2, whiteSpace: 'pre-wrap' }}>
                    {JSON.stringify(entry.model_params, null)}
                  </Typography>
                </>
              )}
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </>
  );
};

// Define types based on the columns array
type SortableColumn = Extract<keyof DeepResearch, typeof columns[number]['id']> & {
    [K in typeof columns[number]['id']]: Extract<typeof columns[number], { id: K }>['sortable'] extends true ? K : never
}[typeof columns[number]['id']];

type FilterableColumn = Extract<keyof DeepResearch, typeof columns[number]['id']> & {
    [K in typeof columns[number]['id']]: Extract<typeof columns[number], { id: K }>['filterable'] extends true ? K : never
}[typeof columns[number]['id']];    

const ResearchEntriesPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { deepResearchApi, organizationsApi } = useApi();
  
  // Ref to track if we've already redirected
  const hasRedirectedRef = React.useRef(false);
  
  // For runtime reference, compute the actual column IDs
  const sortableColumnIds = columns
    .filter(column => column.sortable)
    .map(column => column.id);
  
  const filterableColumnIds = columns
    .filter(column => column.filterable)
    .map(column => column.id);
  
  // Parse and validate orderBy - check against actual sortable columns
  const queryOrderByParam = searchParams.get('orderBy') as string | null;
  const queryOrderBy: SortableColumn = queryOrderByParam && sortableColumnIds.includes(queryOrderByParam as keyof DeepResearch) 
    ? queryOrderByParam as SortableColumn
    : 'created_at';
  
  // Parse and validate order
  const queryOrderParam = searchParams.get('order');
  const queryOrder: Order = queryOrderParam === 'asc' || queryOrderParam === 'desc' 
    ? queryOrderParam 
    : 'desc';
  
  const queryOrgId = searchParams.get('orgId') ? Number(searchParams.get('orgId')) : undefined;
  
  // Filter parameters - only keep valid filterable columns
  const initialFilters: Partial<Record<FilterableColumn, string>> = {};
  Array.from(searchParams.entries()).forEach(([key, value]) => {
    if (filterableColumnIds.includes(key as keyof DeepResearch)) {
      initialFilters[key as FilterableColumn] = value;
    }
  });

  // If queryOrgId is present, ensure visibility is set to 'org'
  if (queryOrgId !== undefined) {
    initialFilters.visibility = 'org';
  }
  
  // Initialize state
  const [entries, setEntries] = useState<DeepResearch[]>([]);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [orgNameMap, setOrgNameMap] = useState<Record<number, string>>({});
  const [initialLoading, setInitialLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(20);
  const [orderBy, setOrderBy] = useState<SortableColumn>(queryOrderBy);
  const [order, setOrder] = useState<Order>(queryOrder);
  const [filters, setFilters] = useState<Partial<Record<FilterableColumn, string>>>(initialFilters);
  const [selectedOrgId, setSelectedOrgId] = useState<number | undefined>(queryOrgId);
  const [organizationsLoaded, setOrganizationsLoaded] = useState(false);
  const isFetchingRef = React.useRef(false);
  
  // Redirect to clean URL if we came in with query params
  useEffect(() => {
    if (searchParams.toString() && !hasRedirectedRef.current) {
      hasRedirectedRef.current = true;
      navigate('/research/entries', { replace: true });
    }
  }, [searchParams, navigate]);
  
  const fetchEntries = async () => {
    // Skip if already fetching
    if (isFetchingRef.current) return;
    
    try {
      isFetchingRef.current = true;
      // Only set refreshing state if we already have data
      if (!initialLoading) {
        setIsRefreshing(true);
      }
      
      const response = await deepResearchApi.getResearchItems({
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
      setEntries(response);
    } catch (error) {
      console.error('Error fetching entries:', error);
    } finally {
      setInitialLoading(false);
      setIsRefreshing(false);
      isFetchingRef.current = false;
    }
  };

  // Only fetch entries when organizations are loaded
  useEffect(() => {
    if (organizationsLoaded) {
      fetchEntries();
    }
  }, [page, rowsPerPage, filters, selectedOrgId, organizationsLoaded, orderBy, order]);

  // Load organizations and validate selectedOrgId
  useEffect(() => {
    const loadOrgs = async () => {
      try {
        const orgs = await organizationsApi.getOrganizations();
        setOrganizations(orgs);
        
        // Create organization name lookup map
        const lookup = orgs.reduce((acc, org) => {
          if (org.id !== undefined) {
            acc[org.id] = org.name;
          }
          return acc;
        }, {} as Record<number, string>);
        setOrgNameMap(lookup);
        
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
        
        setOrganizationsLoaded(true);
      } catch (error) {
        console.error('Error loading organizations:', error);
        setOrganizationsLoaded(true); // Still mark as loaded to avoid infinite loading
      }
    };
    loadOrgs();
  }, [selectedOrgId, filters.visibility]);

  // Update handleSort to use the more specific type
  const handleSort = (property: SortableColumn) => {
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
    setPage(0);
  };

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
      <Header subtitle="Research Entries" />

      <NavBar />

      <main style={{ flex: 1, padding: '2rem' }}>
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
              {entries.map((entry) => (
                <EntryRow 
                  key={entry.id} 
                  entry={entry} 
                  orgName={entry.visibility === 'org' && entry.owner_org_id ? 
                    orgNameMap[Number(entry.owner_org_id)] : undefined}
                />
              ))}
            </TableBody>
          </Table>
          <TablePagination
            component="div"
            count={entries.length}
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

export default ResearchEntriesPage; 