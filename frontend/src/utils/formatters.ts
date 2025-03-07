export function formatTimestamp(pgTimestamp: string, options?: Intl.DateTimeFormatOptions): string {
    // Clean up the timestamp string and ensure it's treated as UTC
    // This handles both with and without timezone formats
    let dateStr = pgTimestamp;

    // If the string doesn't already have timezone info (Z or +/-), add Z for UTC
    if (!dateStr.endsWith('Z') && !dateStr.match(/[+-]\d{2}:?\d{2}$/)) {
        dateStr += 'Z';
    }

    // Replace space with T for ISO format if needed
    dateStr = dateStr.replace(' ', 'T');

    // Create the date object
    const date = new Date(dateStr);

    // Default options for a clean, readable format
    // const defaultOptions: Intl.DateTimeFormatOptions = {
    //     year: 'numeric',
    //     month: 'short',
    //     day: 'numeric',
    //     hour: 'numeric',
    //     minute: '2-digit',
    //     second: '2-digit'
    // };

    // Return formatted date in user's locale and timezone
    return options ? date.toLocaleString(undefined, options) : date.toLocaleString();
}