import React from 'react';
import { Typography } from 'antd';

const { Text } = Typography;

interface BrandLogoProps {
  subtitle?: string;
  compact?: boolean;
}

const BrandLogo: React.FC<BrandLogoProps> = ({
  subtitle = 'Secure | Innovate | Grow',
  compact = false,
}) => {
  const fontSize = compact ? 22 : 28;
  const padding = compact ? '8px 12px' : '16px 20px';
  const borderRadius = compact ? 10 : 14;

  return (
    <div
      style={{
        display: 'inline-flex',
        flexDirection: 'column',
        gap: compact ? 4 : 6,
        alignItems: 'flex-start',
        padding,
        borderRadius,
        backgroundColor: '#0f172a',
      }}
    >
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '0.5rem',
          alignItems: 'center',
          lineHeight: 1,
        }}
      >
        <span
          style={{
            color: '#ffffff',
            fontWeight: 800,
            fontSize,
            letterSpacing: '0.18em',
          }}
        >
          KONEZA
        </span>
        <span
          style={{
            color: '#2dd4bf',
            fontWeight: 800,
            fontSize,
            letterSpacing: '0.18em',
          }}
        >
          SYSTEMS
        </span>
      </div>

      <Text style={{ color: '#94a3b8', fontSize: compact ? 12 : 14 }}>
        {subtitle}
      </Text>
    </div>
  );
};

export default BrandLogo;
