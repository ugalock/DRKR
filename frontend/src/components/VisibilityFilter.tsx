import React, { useState, useEffect, useRef } from 'react';
import { 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  SelectChangeEvent,
  Popper,
  Paper,
  MenuList,
  ClickAwayListener,
  Grow
} from '@mui/material';
import { Organization } from '../types/organization';

const VisibilityFilter: React.FC<{
  value: string;
  onChange: (value: string, orgId?: number) => void;
  organizations: Organization[];
  selectedOrgId?: number;
}> = ({ value, onChange, organizations, selectedOrgId: externalSelectedOrgId }) => {
  const [, setSelectedOrgId] = useState<number | undefined>(externalSelectedOrgId);
  const [subMenuOpen, setSubMenuOpen] = useState(false);
  const orgMenuItemRef = useRef<HTMLLIElement>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  // Keep internal state in sync with external props
  useEffect(() => {
    setSelectedOrgId(externalSelectedOrgId);
  }, [externalSelectedOrgId]);

  // Clean up timeout on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const handleSelectChange = (e: SelectChangeEvent<string>) => {
    const value = e.target.value;
    if (value !== 'org') {
      onChange(value);
      // Reset selectedOrgId when not selecting an org
      setSelectedOrgId(undefined);
    }
  };

  const handleOrgSelect = (orgId?: number) => {
    onChange('org', orgId);
    setSelectedOrgId(orgId);
    setSubMenuOpen(false);
  };

  const handleMouseEnter = () => {
    // Clear any existing timeout to prevent closing
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    setSubMenuOpen(true);
  };

  const handleMouseLeave = () => {
    // Set a timeout to close the menu, but store the ID so we can cancel it if needed
    timeoutRef.current = setTimeout(() => {
      setSubMenuOpen(false);
      timeoutRef.current = null;
    }, 100);
  };

  // When the sub-menu is open, we need to listen for clicks outside to close it
  const handleClickAway = (event: MouseEvent | TouchEvent) => {
    if (orgMenuItemRef.current && !orgMenuItemRef.current.contains(event.target as Node)) {
      setSubMenuOpen(false);
    }
  };

  return (
    <>
      <FormControl size="small" sx={{ minWidth: 120 }}>
        <InputLabel id="visibility-filter-label">Visibility</InputLabel>
        <Select
          labelId="visibility-filter-label"
          value={value}
          label="Visibility"
          onChange={handleSelectChange}
        >
          <MenuItem value="">All</MenuItem>
          <MenuItem value="private">Private</MenuItem>
          <MenuItem value="public">Public</MenuItem>
          <MenuItem 
            ref={orgMenuItemRef}
            value="org"
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            sx={{
              '&:hover': {
                backgroundColor: 'action.hover',
              },
              position: 'relative',
            }}
          >
            Organization
          </MenuItem>
        </Select>
      </FormControl>

      {orgMenuItemRef.current && (
        <Popper
          open={subMenuOpen}
          anchorEl={orgMenuItemRef.current}
          role={undefined}
          placement="right-start"
          transition
          disablePortal
          style={{ zIndex: 1500 }}
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
        >
          {({ TransitionProps }) => (
            <Grow
              {...TransitionProps}
              style={{ transformOrigin: 'left top' }}
            >
              <Paper elevation={3}>
                <ClickAwayListener onClickAway={handleClickAway}>
                  <MenuList autoFocusItem={false}>
                    <MenuItem onClick={() => handleOrgSelect()}>
                      All Organizations
                    </MenuItem>
                    {organizations.map(org => (
                      <MenuItem 
                        key={org.id} 
                        onClick={() => handleOrgSelect(org.id)}
                      >
                        {org.name}
                      </MenuItem>
                    ))}
                  </MenuList>
                </ClickAwayListener>
              </Paper>
            </Grow>
          )}
        </Popper>
      )}
    </>
  );
};

export default VisibilityFilter;