import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { AppBar, Toolbar, Button, Box } from '@mui/material';
import { useAuth } from '../../hooks/useAuth';

const NavBar: React.FC = () => {
  const location = useLocation();
  const { logout, isAuthenticated } = useAuth();

  const isActive = (path: string) => location.pathname === path;

  return (
    <AppBar position="static" color="default" elevation={1}>
      <Toolbar sx={{ display: 'flex', justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            component={Link}
            to="/home"
            color={isActive('/home') ? 'primary' : 'inherit'}
            sx={{ textTransform: 'none' }}
          >
            Home
          </Button>
          <Button
            component={Link}
            to="/research/jobs"
            color={isActive('/research/jobs') ? 'primary' : 'inherit'}
            sx={{ textTransform: 'none' }}
          >
            Research Jobs
          </Button>
        </Box>

        {isAuthenticated && (
          <Button 
            onClick={() => logout()}
            color="inherit"
            sx={{ textTransform: 'none' }}
          >
            Log Out
          </Button>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default NavBar; 