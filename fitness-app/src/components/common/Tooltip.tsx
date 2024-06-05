import React from 'react';

interface TooltipProps {
    children: React.ReactNode;
}

const Tooltip: React.FC<TooltipProps> = ({ children }) => {
    return (
        <div className="absolute bg-white p-2 border rounded shadow-md">
            {children}
        </div>
    );
};

export default Tooltip;
