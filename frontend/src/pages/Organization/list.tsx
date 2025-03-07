import React, { useEffect, useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { 
    Box, 
    Typography, 
    Paper, 
    Container, 
    CircularProgress,
    Divider,
    Button,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField
} from '@mui/material';
import Grid from '@mui/material/Grid2';
import Header from '../../components/common/Header';
import Footer from '../../components/common/Footer';
import NavBar from '../../components/common/NavBar';
import { useApi } from '../../hooks/useApi';
import { Organization } from '../../types/organization';
import { User } from '../../types/user';
import { formatTimestamp } from '../../utils/formatters';
const OrganizationListPage: React.FC = () => {
    const { organizationsApi, userApi } = useApi();
    const [organizations, setOrganizations] = useState<Organization[]>([]);
    const [currentUser, setCurrentUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    
    // Create organization modal state
    const [openCreateModal, setOpenCreateModal] = useState(false);
    const [newOrgName, setNewOrgName] = useState('');
    const [newOrgDescription, setNewOrgDescription] = useState('');
    const [creating, setCreating] = useState(false);
    
    useEffect(() => {
        const fetchUser = async () => {
            if (error) {
                return;
            }
            try {
                setLoading(true);
                // Fetch user data
                const userData = await userApi.getCurrentUser();
                setCurrentUser(userData);
                
                setError(null);
            } catch (err) {
                console.error('Error fetching user:', err);
                setError('Failed to load user. Please try again later.');
            } finally {
                setLoading(false);
            }
        };
        fetchUser();
    }, []);
    // Use useMemo to compute the filtered organizations only when the dependencies change
    const { ownerOrgs, adminOrgs, memberOrgs } = useMemo(() => {
        return {
            ownerOrgs: organizations.filter(org => 
                org.members?.some(m => m.user_id === currentUser?.id && m.role === 'owner')
            ),
            adminOrgs: organizations.filter(org => 
                org.members?.some(m => m.user_id === currentUser?.id && m.role === 'admin')
            ),
            memberOrgs: organizations.filter(org => 
                org.members?.some(m => m.user_id === currentUser?.id && m.role === 'member')
            )
        };
    }, [organizations, currentUser]);
    
    const fetchOrgs = async () => {
        if (error) {
            return;
        }
        try {
            // Fetch organizations
            const orgData = await organizationsApi.getOrganizations();
            setOrganizations(orgData);
            
            setError(null);
        } catch (err) {
            console.error('Error fetching organizations:', err);
            setError('Failed to load organizations. Please try again later.');
        }
    };
    
    useEffect(() => {
        fetchOrgs();
    }, [creating]);
    
    const handleOpenCreateModal = () => {
        setNewOrgName('');
        setNewOrgDescription('');
        setOpenCreateModal(true);
    };
    
    const handleCloseCreateModal = () => {
        setOpenCreateModal(false);
    };
    
    const handleCreateOrganization = async () => {
        try {
            await organizationsApi.createOrganization({
                name: newOrgName,
                description: newOrgDescription
            });
            
            // Close the modal and refresh orgs
            handleCloseCreateModal();
            setCreating(true);
        } catch (err) {
            console.error('Error creating organization:', err);
            setError('Failed to create organization. Please try again.');
        } finally {
            setCreating(false);
        }
    };
    
    // Helper function to format the organization card
    const renderOrgCard = (org: Organization) => {
        const userMembership = org.members?.find(m => m.user_id === currentUser?.id);
        const memberCount = org.members?.length || 0;
        const joinedDate = userMembership?.created_at ? 
            formatTimestamp(userMembership.created_at) : 'Unknown';
        
        return (
            <Box key={org.id} mb={2}>
                <Typography variant="h6" component="div">
                    <Link to={`/organizations/${org.id}`} style={{ textDecoration: 'none', color: 'primary' }}>
                        {org.name}
                    </Link>
                    {' - '}
                    <Typography component="span" variant="body1" color="text.secondary">
                        {memberCount} member{memberCount !== 1 ? 's' : ''} - Joined: {joinedDate}
                    </Typography>
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ pt: 1 }}>
                    {org.description || 'No description provided.'}
                </Typography>
            </Box>
        );
    };
    
    return (
        <>
            <Header subtitle="Organizations"/>
            <NavBar />
            <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="h4" component="h1" sx={{ pl: 4 }}>
                        My Organizations
                    </Typography>
                    <Button 
                        variant="contained" 
                        color="primary" 
                        onClick={handleOpenCreateModal}
                    >
                        Create Organization
                    </Button>
                </Box>
                
                {loading ? (
                    <Box display="flex" justifyContent="center" my={4}>
                        <CircularProgress />
                    </Box>
                ) : error ? (
                    <Paper sx={{ p: 3, mb: 3 }}>
                        <Typography color="error">{error}</Typography>
                    </Paper>
                ) : (
                    <Grid container spacing={3}>
                        <Grid size={{ xs: 12 }}>
                            {ownerOrgs.length > 0 && (
                                <Paper sx={{ p: 3, mb: 3 }}>
                                    <Typography variant="h5" component="h2" gutterBottom>
                                        Owned Organizations
                                    </Typography>
                                    <Divider sx={{ mb: 2 }} />
                                    {ownerOrgs.map(renderOrgCard)}
                                </Paper>
                            )}
                            
                            {adminOrgs.length > 0 && (
                                <Paper sx={{ p: 3, mb: 3 }}>
                                    <Typography variant="h5" component="h2" gutterBottom>
                                        Administered Organizations
                                    </Typography>
                                    <Divider sx={{ mb: 2 }} />
                                    {adminOrgs.map(renderOrgCard)}
                                </Paper>
                            )}
                            
                            {memberOrgs.length > 0 && (
                                <Paper sx={{ p: 3, mb: 3 }}>
                                    <Typography variant="h5" component="h2" gutterBottom>
                                        Member Organizations
                                    </Typography>
                                    <Divider sx={{ mb: 2 }} />
                                    {memberOrgs.map(renderOrgCard)}
                                </Paper>
                            )}
                            
                            {organizations.length === 0 && (
                                <Paper sx={{ p: 3, mb: 3 }}>
                                    <Typography>
                                        You are not a member of any organizations yet.
                                    </Typography>
                                </Paper>
                            )}
                        </Grid>
                    </Grid>
                )}
                
                {/* Create Organization Modal */}
                <Dialog open={openCreateModal} onClose={handleCloseCreateModal} maxWidth="sm" fullWidth>
                    <DialogTitle>Create New Organization</DialogTitle>
                    <DialogContent>
                        <TextField
                            autoFocus
                            margin="dense"
                            label="Organization Name"
                            type="text"
                            fullWidth
                            variant="outlined"
                            value={newOrgName}
                            onChange={(e) => setNewOrgName(e.target.value)}
                            required
                        />
                        <TextField
                            margin="dense"
                            label="Description"
                            type="text"
                            fullWidth
                            variant="outlined"
                            multiline
                            rows={3}
                            value={newOrgDescription}
                            onChange={(e) => setNewOrgDescription(e.target.value)}
                            required
                        />
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={handleCloseCreateModal} disabled={creating}>Cancel</Button>
                        <Button 
                            onClick={handleCreateOrganization} 
                            color="primary" 
                            disabled={!newOrgName || !newOrgDescription || creating}
                        >
                            {creating ? 'Creating...' : 'Create'}
                        </Button>
                    </DialogActions>
                </Dialog>
            </Container>
            <Footer />
        </>
    );
};

export default OrganizationListPage; 