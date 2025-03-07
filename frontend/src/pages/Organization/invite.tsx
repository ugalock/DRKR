import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
    Box, 
    Typography, 
    Container, 
    Paper, 
    CircularProgress,
    Alert
} from '@mui/material';

import Header from '../../components/common/Header';
import Footer from '../../components/common/Footer';
import NavBar from '../../components/common/NavBar';
import { useApi } from '../../hooks/useApi';
import { AcceptInviteResponse } from '../../types/organization_invite';

const InviteAcceptPage: React.FC = () => {
    const { token } = useParams<{ token: string }>();
    const navigate = useNavigate();
    const { organizationInvitesApi } = useApi();
    
    const [loading, setLoading] = useState(true);
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [message, setMessage] = useState('');
    
    useEffect(() => {
        const acceptInvite = async () => {
            if (!token) {
                setError('Invalid invite token');
                setLoading(false);
                return;
            }
            
            try {
                const response: AcceptInviteResponse = await organizationInvitesApi.acceptInvite(token);
                setMessage(response.message);
                setSuccess(true);
                
                // Redirect after a short delay to allow the user to see the success message
                setTimeout(() => {
                    navigate(`/organizations/${response.organization_id}`);
                }, 2000);
            } catch (err) {
                console.error('Error accepting invite:', err);
                setError('Failed to accept invite. The invite may be invalid or already used.');
            } finally {
                setLoading(false);
            }
        };
        
        acceptInvite();
    }, [token, navigate]);
    
    return (
        <>
            <Header />
            <NavBar />
            <Container maxWidth="md" sx={{ mt: 8, mb: 8 }}>
                <Paper sx={{ p: 4, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    {loading ? (
                        <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
                            <CircularProgress />
                            <Typography variant="h6">Processing your invitation...</Typography>
                        </Box>
                    ) : success ? (
                        <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
                            <Alert severity="success" sx={{ width: '100%' }}>
                                {message}
                            </Alert>
                            <Typography variant="body1">
                                Redirecting you to the organization page...
                            </Typography>
                        </Box>
                    ) : (
                        <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
                            <Alert severity="error" sx={{ width: '100%' }}>
                                {error}
                            </Alert>
                            <Typography variant="body1">
                                Please check your invitation link and try again.
                            </Typography>
                        </Box>
                    )}
                </Paper>
            </Container>
            <Footer />
        </>
    );
};

export default InviteAcceptPage;
