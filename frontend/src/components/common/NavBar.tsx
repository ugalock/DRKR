import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { AppBar, Toolbar, Button, Box, IconButton, Tooltip } from '@mui/material';
import LogoutIcon from '@mui/icons-material/Logout';
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
            to="/organizations"
            color={isActive('/organizations') ? 'primary' : 'inherit'}
            sx={{ textTransform: 'none' }}
          >
            Organizations
          </Button>
          <Button
            component={Link}
            to="/research/jobs"
            color={isActive('/research/jobs') ? 'primary' : 'inherit'}
            sx={{ textTransform: 'none' }}
          >
            Research Jobs
          </Button>
          <Button
            component={Link}
            to="/research/entries"
            color={isActive('/research/entries') ? 'primary' : 'inherit'}
            sx={{ textTransform: 'none' }}
          >
            Deep Research
          </Button>
        </Box>

        {isAuthenticated && (
          <Tooltip title="Log out">
            <IconButton 
              onClick={() => logout()}
              color="inherit"
              edge="end"
            >
              <LogoutIcon />
            </IconButton>
          </Tooltip>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default NavBar; 