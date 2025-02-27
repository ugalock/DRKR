const Footer = () => {
    return (
        <footer className="bg-white border-t">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                <div className="text-center text-sm text-gray-500">
                    © {new Date().getFullYear()} DRKR. All rights reserved.
                </div>
            </div>
        </footer>
    );
};

export default Footer;