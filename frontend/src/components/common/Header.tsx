import { Typography } from "@mui/material";

const Header = ({ subtitle }: { subtitle?: string }) => {
    return (
        <header style={{ padding: '1rem', borderBottom: '1px solid #ccc' }}>
            <Typography variant="h4">DRKR</Typography>
            {subtitle && <Typography variant="h6">{subtitle}</Typography>}
        </header>
    );
};

export default Header;