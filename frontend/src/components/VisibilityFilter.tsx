import React, { useState, useEffect, useRef } from 'react';
import {
  FormControl,
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
  showAllOption?: boolean;
  showAllOrganizationsOption?: boolean;
  loadingOrganizations?: boolean;
}> = ({
  value,
  onChange,
  organizations,
  selectedOrgId: externalSelectedOrgId,
  showAllOption = true,
  showAllOrganizationsOption = true,
  loadingOrganizations = false
}) => {
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
        <FormControl size="small" sx={{ minWidth: 120 }} disabled={loadingOrganizations}>
          <Select
            value={value}
            onChange={handleSelectChange}
          >
            {showAllOption && <MenuItem value="">All</MenuItem>}
            <MenuItem value="private">Private</MenuItem>
            <MenuItem value="public">Public</MenuItem>
            <MenuItem
              ref={orgMenuItemRef}
              value="org"
              onMouseEnter={organizations?.length ? handleMouseEnter : undefined}
              onMouseLeave={organizations?.length ? handleMouseLeave : undefined}
              disabled={!organizations?.length}
              sx={{
                '&:hover': {
                  backgroundColor: organizations?.length ? 'action.hover' : undefined,
                },
                position: 'relative',
              }}
            >
              Organization
            </MenuItem>
          </Select>
        </FormControl>

        {orgMenuItemRef.current && organizations?.length > 0 && (
          <Popper
            open={subMenuOpen}
            anchorEl={{
              getBoundingClientRect() {
                const rect = orgMenuItemRef.current!.getBoundingClientRect();
                // Create a proper DOMRect that includes all required methods
                return new DOMRect(
                  rect.right, // x position at the right edge of menu item
                  rect.top,   // y position at the top of menu item
                  0,          // width (zero for a precise point)
                  0           // height (zero for a precise point)
                );
              }
            }}
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
                      {showAllOrganizationsOption && (
                        <MenuItem onClick={() => handleOrgSelect()}>
                          All Organizations
                        </MenuItem>
                      )}
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