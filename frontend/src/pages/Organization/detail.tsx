import React, { useEffect, useState, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
    Box, 
    Typography, 
    Container, 
    Paper, 
    CircularProgress, 
    Tabs, 
    Tab, 
    Button,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    IconButton,
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Stack,
    Chip,
    TextField,
    Autocomplete
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import LaunchIcon from '@mui/icons-material/Launch';
import Header from '../../components/common/Header';
import Footer from '../../components/common/Footer';
import NavBar from '../../components/common/NavBar';
import { useApi } from '../../hooks/useApi';
import { Organization, OrganizationMember } from '../../types/organization';
import { ApiKey } from '../../types/api_key';
import { User } from '../../types/user';
import { OrganizationInvite, OrganizationInviteRequest } from '../../types/organization_invite';
import { formatTimestamp } from '../../utils/formatters';

interface TabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
}

function TabPanel(props: TabPanelProps) {
    const { children, value, index, ...other } = props;

    return (
        <div
            role="tabpanel"
            hidden={value !== index}
            id={`org-tabpanel-${index}`}
            aria-labelledby={`org-tab-${index}`}
            {...other}
        >
            {value === index && (
                <Box sx={{ p: 3 }}>
                    {children}
                </Box>
            )}
        </div>
    );
}

function a11yProps(index: number) {
    return {
        id: `org-tab-${index}`,
        'aria-controls': `org-tabpanel-${index}`,
    };
}

const OrganizationDetailPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const { organizationsApi, apiKeysApi, userApi, organizationInvitesApi } = useApi();
    const [organization, setOrganization] = useState<Organization | null>(null);
    const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
    const [invites, setInvites] = useState<OrganizationInvite[]>([]);
    const [currentUser, setCurrentUser] = useState<User | null>(null);
    const [orgUsers, setOrgUsers] = useState<Record<number, User>>({});
    const [loading, setLoading] = useState(true);
    const [invitesLoading, setInvitesLoading] = useState(false);
    const [updating, setUpdating] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [tabValue, setTabValue] = useState(0);
    
    // Dialog states
    const [openRoleDialog, setOpenRoleDialog] = useState(false);
    const [openRemoveDialog, setOpenRemoveDialog] = useState(false);
    const [selectedMember, setSelectedMember] = useState<OrganizationMember | null>(null);
    const [newRole, setNewRole] = useState('');
    
    // Invite dialog states
    const [openInviteDialog, setOpenInviteDialog] = useState(false);
    const [inviteRole, setInviteRole] = useState('member');
    const [selectedUser, setSelectedUser] = useState<User | null>(null);
    const [searchUsers, setSearchUsers] = useState<User[]>([]);
    const [userSearchLoading, setUserSearchLoading] = useState(false);
    const [userSearchInput, setUserSearchInput] = useState('');
    
    // Use useMemo for computed values that depend on state
    const {
        isOwner,
        isAdmin,
        canManageMembers,
        sortedMembers
    } = useMemo(() => {
        const currentUserMembership = organization?.members?.find(m => m.user_id === currentUser?.id);
        const isOwner = currentUserMembership?.role === 'owner';
        const isAdmin = currentUserMembership?.role === 'admin';
        const canManageMembers = isOwner || isAdmin;
        
        // Sort members by role and then by join date
        const sortedMembers = organization?.members?.slice() || [];
        sortedMembers.sort((a, b) => {
            const roleOrder = { owner: 0, admin: 1, member: 2 };
            const roleA = a.role || 'member';
            const roleB = b.role || 'member';
            
            // First compare by role
            if (roleOrder[roleA as keyof typeof roleOrder] !== roleOrder[roleB as keyof typeof roleOrder]) {
                return roleOrder[roleA as keyof typeof roleOrder] - roleOrder[roleB as keyof typeof roleOrder];
            }
            
            // Then by join date (most recent first)
            return new Date(b.created_at || '').getTime() - new Date(a.created_at || '').getTime();
        });
        
        return {
            currentUserMembership,
            isOwner,
            isAdmin,
            canManageMembers,
            sortedMembers
        };
    }, [organization, currentUser, orgUsers]);

    const fetchData = async () => {
        if (!id) return;
        
        try {
            setLoading(true);
            
            // Fetch organization data
            const orgData = await organizationsApi.getOrganization(parseInt(id));
            setOrganization(orgData);

            // Fetch user data
            const userData = await userApi.getCurrentUser();
            setCurrentUser(userData);
            
            // Fetch API keys for this organization
            const keysData = await apiKeysApi.getApiKeys(parseInt(id));
            setApiKeys(keysData);
            
            // Fetch users for this organization
            const usersData = await userApi.getUsers({ org_id: parseInt(id) });
            setOrgUsers(usersData.reduce((acc, user) => {
                acc[user.id] = user;
                return acc;
            }, {} as Record<number, User>));
            
            setError(null);
        } catch (err) {
            console.error('Error fetching data:', err);
            setError('Failed to load data. Please try again later.');
        } finally {
            setLoading(false);
        }
    };
    
    useEffect(() => {
        fetchData();
    }, [id, updating]);

    const fetchInvites = async () => {
        if (!id || !canManageMembers) return;

        try {
            setInvitesLoading(true);
            const invitesData = await organizationInvitesApi.listInvites(parseInt(id));
            setInvites(invitesData);
        } catch (err) {
            console.error('Error fetching invites:', err);
        } finally {
            setInvitesLoading(false);
        }
    };

    useEffect(() => {
        if (!organization || !canManageMembers) return;
        // Fetch invites for this organization if admin or owner
        fetchInvites();
    }, [organization, canManageMembers]);
    
    const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
        setTabValue(newValue);
    };
    
    const handleOpenRoleDialog = (member: OrganizationMember) => {
        setSelectedMember(member);
        setNewRole(member.role || 'member');
        setOpenRoleDialog(true);
    };
    
    const handleCloseRoleDialog = () => {
        setOpenRoleDialog(false);
        setSelectedMember(null);
    };
    
    const handleOpenRemoveDialog = (member: OrganizationMember) => {
        setSelectedMember(member);
        setOpenRemoveDialog(true);
    };
    
    const handleCloseRemoveDialog = () => {
        setOpenRemoveDialog(false);
        setSelectedMember(null);
    };
    
    const handleRoleChange = async () => {
        if (!selectedMember || !organization?.id) return;
        
        try {
            await organizationsApi.updateMemberRole(
                organization.id,
                selectedMember.user_id!,
                { role: newRole }
            );
            
            setUpdating(true);
            
            handleCloseRoleDialog();
        } catch (err) {
            console.error('Error updating member role:', err);
            setError('Failed to update member role. Please try again later.');
        } finally {
            setUpdating(false);
        }
    };
    
    const handleRemoveMember = async () => {
        if (!selectedMember || !organization?.id) return;
        
        try {
            await organizationsApi.removeMember(organization.id, selectedMember.user_id!);
            
            // Refresh organization data
            const updatedOrgData = await organizationsApi.getOrganization(organization.id);
            setOrganization(updatedOrgData);
            
            handleCloseRemoveDialog();
        } catch (err) {
            console.error('Error removing member:', err);
            setError('Failed to remove member. Please try again later.');
        }
    };
    
    // Check if current user can edit a member's role
    const canEditMemberRole = (member: OrganizationMember) => {
        if (member.user_id === currentUser?.id) return false; // Can't edit own role
        
        if (isOwner) return true; // Owners can edit anyone
        
        if (isAdmin) {
            // Admins can only edit members, not other admins or owners
            return member.role === 'member';
        }
        
        return false;
    };
    
    // Check if current user can remove a member
    const canRemoveMember = (member: OrganizationMember) => {
        if (member.user_id === currentUser?.id) return true; // Can remove self
        
        if (isOwner) {
            // Owners can remove anyone except the last owner
            if (member.role === 'owner') {
                const ownerCount = organization?.members?.filter(m => m.role === 'owner').length || 0;
                return ownerCount > 1;
            }
            return true;
        }
        
        if (isAdmin) {
            // Admins can only remove members, not other admins or owners
            return member.role === 'member';
        }
        
        return false;
    };
    
    const handleOpenInviteDialog = () => {
        setOpenInviteDialog(true);
        setInviteRole('member');
        setSelectedUser(null);
        setUserSearchInput('');
        setSearchUsers([]);
    };
    
    const handleCloseInviteDialog = () => {
        setOpenInviteDialog(false);
    };
    
    const handleSearchUsers = async (searchTerm: string) => {
        if (!searchTerm || searchTerm.length < 2) {
            setSearchUsers([]);
            return;
        }
        
        try {
            setUserSearchLoading(true);
            const users = await userApi.getUsers({ 
                search: searchTerm,
                page: 1,
                limit: 10
            });
            setSearchUsers(users);
        } catch (err) {
            console.error('Error searching users:', err);
        } finally {
            setUserSearchLoading(false);
        }
    };
    
    const handleUserInputChange = (_event: React.SyntheticEvent, value: string) => {
        setUserSearchInput(value);
        handleSearchUsers(value);
    };
    
    const handleUserSelect = (_event: React.SyntheticEvent, value: User | null) => {
        setSelectedUser(value);
    };
    
    const handleCreateInvite = async () => {
        if (!selectedUser || !organization?.id) return;
        
        try {
            const inviteRequest: OrganizationInviteRequest = {
                invited_user_id: selectedUser.id,
                role: inviteRole
            };
            
            const response = await organizationInvitesApi.createInvite(organization.id, inviteRequest);
            
            if (response && 'detail' in response) {
                setError(response.detail);
            } else {
                // Refresh invites
                await fetchInvites();
            }
            
            handleCloseInviteDialog();
        } catch (err) {
            console.error('Error creating invite:', err);
            setError('Failed to create invite. Please try again later.');
        }
    };
    
    const handleDeleteInvite = async (inviteId: number) => {
        if (!organization?.id) return;
        
        try {
            await organizationInvitesApi.deleteInvite(organization.id, inviteId);
            
            // Refresh invites
            await fetchInvites();
        } catch (err) {
            console.error('Error deleting invite:', err);
            setError('Failed to delete invite. Please try again later.');
        }
    };
    
    if (loading) {
        return (
            <>
                <Header />
                <NavBar />
                <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
                    <Box display="flex" justifyContent="center" my={4}>
                        <CircularProgress />
                    </Box>
                </Container>
                <Footer />
            </>
        );
    }
    
    if (error || !organization) {
        return (
            <>
                <Header />
                <NavBar />
                <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
                    <Paper sx={{ p: 3 }}>
                        <Typography color="error">
                            {error || 'Organization not found'}
                        </Typography>
                    </Paper>
                </Container>
                <Footer />
            </>
        );
    }
    
    return (
        <>
            <Header />
            <NavBar />
            <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom>
                    {organization.name}
                </Typography>
                
                {organization.description && (
                    <Typography variant="body1" component="p">
                        {organization.description}
                    </Typography>
                )}
                
                <Box sx={{ borderBottom: 1, borderColor: 'divider', display: 'flex', alignItems: 'center' }}>
                    <Tabs 
                        value={tabValue} 
                        onChange={handleTabChange} 
                        aria-label="organization tabs"
                        sx={{ flexGrow: 1 }}
                    >
                        <Tab label="Members" {...a11yProps(0)} />
                        <Tab label="API Keys" {...a11yProps(1)} />
                        {canManageMembers && <Tab label="Invites" {...a11yProps(2)} />}
                    </Tabs>
                    
                    {/* Links to research pages */}
                    <Box sx={{ display: 'flex', gap: 2, ml: 2 }}>
                        <Button 
                            component={Link} 
                            to={`/research/jobs?orgId=${organization.id}`}
                            variant="outlined"
                            size="small"
                            endIcon={<LaunchIcon />}
                        >
                            Org Research Jobs
                        </Button>
                        <Button 
                            component={Link} 
                            to={`/research/entries?orgId=${organization.id}`}
                            variant="outlined"
                            size="small"
                            endIcon={<LaunchIcon />}
                        >
                            Org Research Entries
                        </Button>
                    </Box>
                </Box>
                
                <TabPanel value={tabValue} index={0}>
                    <TableContainer>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell>Role</TableCell>
                                    <TableCell>Username</TableCell>
                                    <TableCell>Email</TableCell>
                                    <TableCell>Date Joined</TableCell>
                                    <TableCell align="right">Actions</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {sortedMembers.map((member) => {
                                    const joinDate = member.created_at ? 
                                        formatTimestamp(member.created_at) : 'Unknown';
                                    const orgUser = orgUsers[member.user_id!];
                                    const userDisplayName = orgUser?.display_name || orgUser?.username || `User ${member.user_id}`;
                                    return (
                                        <TableRow key={member.id}>
                                            <TableCell>
                                                <Chip 
                                                    label={member.role} 
                                                    color={
                                                        member.role === 'owner' ? 'primary' : 
                                                        member.role === 'admin' ? 'secondary' : 'default'
                                                    }
                                                    size="small"
                                                />
                                            </TableCell>
                                            <TableCell>{userDisplayName}</TableCell>
                                            <TableCell>{orgUser?.email || '-'}</TableCell>
                                            <TableCell>{joinDate}</TableCell>
                                            <TableCell align="right">
                                                <Stack direction="row" spacing={1} justifyContent="flex-end">
                                                    {canEditMemberRole(member) && (
                                                        <IconButton 
                                                            size="small" 
                                                            color="primary"
                                                            onClick={() => handleOpenRoleDialog(member)}
                                                        >
                                                            <EditIcon fontSize="small" />
                                                        </IconButton>
                                                    )}
                                                    {canRemoveMember(member) && (
                                                        <IconButton 
                                                            size="small" 
                                                            color="error"
                                                            onClick={() => handleOpenRemoveDialog(member)}
                                                        >
                                                            <DeleteIcon fontSize="small" />
                                                        </IconButton>
                                                    )}
                                                </Stack>
                                            </TableCell>
                                        </TableRow>
                                    );
                                })}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </TabPanel>
                
                <TabPanel value={tabValue} index={1}>
                    <TableContainer>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell>Service</TableCell>
                                    <TableCell>Token</TableCell>
                                    <TableCell>Created</TableCell>
                                    <TableCell>Expires</TableCell>
                                    <TableCell align="right">Actions</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {apiKeys.map((key) => {
                                    const createdDate = key.created_at ? 
                                        formatTimestamp(key.created_at) : 'Unknown';
                                    const expiresDate = key.expires_at ? 
                                        formatTimestamp(key.expires_at) : 'Never';
                                    
                                    return (
                                        <TableRow key={key.id}>
                                            <TableCell>{key.api_service?.name || 'Unknown'}</TableCell>
                                            <TableCell>
                                                <Typography 
                                                    variant="body2" 
                                                    sx={{ 
                                                        fontFamily: 'monospace',
                                                        maxWidth: '150px',
                                                        overflow: 'hidden',
                                                        textOverflow: 'ellipsis',
                                                        whiteSpace: 'nowrap'
                                                    }}
                                                >
                                                    {key.token}
                                                </Typography>
                                            </TableCell>
                                            <TableCell>{createdDate}</TableCell>
                                            <TableCell>{expiresDate}</TableCell>
                                            <TableCell align="right">
                                                {canManageMembers && (
                                                    <IconButton 
                                                        size="small" 
                                                        color="error"
                                                        onClick={() => apiKeysApi.revokeApiKey(key.id)}
                                                    >
                                                        <DeleteIcon fontSize="small" />
                                                    </IconButton>
                                                )}
                                            </TableCell>
                                        </TableRow>
                                    );
                                })}
                                
                                {apiKeys.length === 0 && (
                                    <TableRow>
                                        <TableCell colSpan={5} align="center">
                                            <Typography variant="body2" color="text.secondary">
                                                No API keys found for this organization.
                                            </Typography>
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                        
                        {canManageMembers && (
                            <Box mt={2} display="flex" justifyContent="flex-end">
                                <Button 
                                    variant="contained" 
                                    component={Link}
                                    to={`/api-keys/new?orgId=${organization.id}`}
                                >
                                    Create New API Key
                                </Button>
                            </Box>
                        )}
                    </TableContainer>
                </TabPanel>
                
                {canManageMembers && (
                    <TabPanel value={tabValue} index={2}>
                        <TableContainer>
                            <Table>
                                <TableHead>
                                    <TableRow>
                                        <TableCell>User</TableCell>
                                        <TableCell>Role</TableCell>
                                        <TableCell>Created</TableCell>
                                        <TableCell>Expires</TableCell>
                                        <TableCell align="right">Actions</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {invitesLoading ? (
                                        <TableRow>
                                            <TableCell colSpan={5} align="center">
                                                <CircularProgress size={24} />
                                            </TableCell>
                                        </TableRow>
                                    ) : invites.length > 0 ? (
                                        invites.map((invite) => {
                                            const createdDate = invite.created_at ? 
                                                formatTimestamp(invite.created_at) : 'Unknown';
                                            const expiresDate = invite.expires_at ? 
                                                formatTimestamp(invite.expires_at) : 'Never';
                                            
                                            return (
                                                <TableRow key={invite.id}>
                                                    <TableCell>{invite.invited_user_name}</TableCell>
                                                    <TableCell>
                                                        <Chip 
                                                            label={invite.role} 
                                                            color={
                                                                invite.role === 'owner' ? 'primary' : 
                                                                invite.role === 'admin' ? 'secondary' : 'default'
                                                            }
                                                            size="small"
                                                        />
                                                    </TableCell>
                                                    <TableCell>{createdDate}</TableCell>
                                                    <TableCell>{expiresDate}</TableCell>
                                                    <TableCell align="right">
                                                        <IconButton 
                                                            size="small" 
                                                            color="error"
                                                            onClick={() => handleDeleteInvite(invite.id)}
                                                        >
                                                            <DeleteIcon fontSize="small" />
                                                        </IconButton>
                                                    </TableCell>
                                                </TableRow>
                                            );
                                        })
                                    ) : (
                                        <TableRow>
                                            <TableCell colSpan={5} align="center">
                                                <Typography variant="body2" color="text.secondary">
                                                    No pending invites found for this organization.
                                                </Typography>
                                            </TableCell>
                                        </TableRow>
                                    )}
                                </TableBody>
                            </Table>
                            
                            <Box mt={2} display="flex" justifyContent="flex-end">
                                <Button 
                                    variant="contained" 
                                    onClick={handleOpenInviteDialog}
                                >
                                    Create Invite
                                </Button>
                            </Box>
                        </TableContainer>
                    </TabPanel>
                )}
                
                {/* Role change dialog */}
                <Dialog open={openRoleDialog} onClose={handleCloseRoleDialog}>
                    <DialogTitle>Change Member Role</DialogTitle>
                    <DialogContent>
                        <DialogContentText>
                            Select a new role for this member:
                        </DialogContentText>
                        <FormControl fullWidth margin="normal">
                            <InputLabel id="role-select-label">Role</InputLabel>
                            <Select
                                labelId="role-select-label"
                                value={newRole}
                                label="Role"
                                onChange={(e) => setNewRole(e.target.value)}
                            >
                                {isOwner && <MenuItem value="owner">Owner</MenuItem>}
                                {(isOwner || isAdmin) && <MenuItem value="admin">Admin</MenuItem>}
                                <MenuItem value="member">Member</MenuItem>
                            </Select>
                        </FormControl>
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={handleCloseRoleDialog}>Cancel</Button>
                        <Button onClick={handleRoleChange} color="primary">
                            Update Role
                        </Button>
                    </DialogActions>
                </Dialog>
                
                {/* Remove member dialog */}
                <Dialog open={openRemoveDialog} onClose={handleCloseRemoveDialog}>
                    <DialogTitle>Remove Member</DialogTitle>
                    <DialogContent>
                        <DialogContentText>
                            Are you sure you want to remove this member from the organization?
                            This action cannot be undone.
                        </DialogContentText>
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={handleCloseRemoveDialog}>Cancel</Button>
                        <Button onClick={handleRemoveMember} color="error">
                            Remove
                        </Button>
                    </DialogActions>
                </Dialog>
                
                {/* Create invite dialog */}
                <Dialog open={openInviteDialog} onClose={handleCloseInviteDialog} fullWidth maxWidth="sm">
                    <DialogTitle>Invite User to Organization</DialogTitle>
                    <DialogContent>
                        <Box my={2}>
                            <Autocomplete
                                options={searchUsers}
                                getOptionLabel={(option) => option.display_name || option.username || `User ${option.id}`}
                                loading={userSearchLoading}
                                inputValue={userSearchInput}
                                onInputChange={handleUserInputChange}
                                onChange={handleUserSelect}
                                isOptionEqualToValue={(option, value) => option.id === value.id}
                                filterOptions={(x) => x} // Disable built-in filtering since we're doing server-side search
                                noOptionsText={userSearchInput.length < 2 ? "Type at least 2 characters" : "No users found"}
                                autoHighlight
                                clearOnEscape
                                blurOnSelect
                                renderInput={(params) => (
                                    <TextField
                                        {...params}
                                        label="Search for a user"
                                        variant="outlined"
                                        fullWidth
                                        InputProps={{
                                            ...params.InputProps,
                                            endAdornment: (
                                                <>
                                                    {userSearchLoading ? <CircularProgress size={20} /> : null}
                                                    {params.InputProps.endAdornment}
                                                </>
                                            ),
                                        }}
                                    />
                                )}
                            />
                        </Box>
                        
                        <FormControl fullWidth margin="normal">
                            <InputLabel id="invite-role-select-label">Role</InputLabel>
                            <Select
                                labelId="invite-role-select-label"
                                value={inviteRole}
                                label="Role"
                                onChange={(e) => setInviteRole(e.target.value)}
                            >
                                {isOwner && <MenuItem value="owner">Owner</MenuItem>}
                                {(isOwner || isAdmin) && <MenuItem value="admin">Admin</MenuItem>}
                                <MenuItem value="member">Member</MenuItem>
                            </Select>
                        </FormControl>
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={handleCloseInviteDialog}>Cancel</Button>
                        <Button 
                            onClick={handleCreateInvite} 
                            color="primary"
                            disabled={!selectedUser}
                        >
                            Create Invite
                        </Button>
                    </DialogActions>
                </Dialog>
            </Container>
            <Footer />
        </>
    );
};

export default OrganizationDetailPage; 