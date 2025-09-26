import {
  Card,
  CardContent,
  Typography,
} from '@mui/material';

const ManageItem: React.FC<{
  title: string;
  description: string;
  icon: React.ReactElement;
  onClick: () => void;
}> = ({ title, description, icon, onClick }) => {
  return (
    <Card
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        p: 2,
        cursor: 'pointer',
        transition: 'transform 0.2s',
        '&:hover': {
          transform: 'scale(1.05)',
        },
      }}
      onClick={onClick}
    >
      {icon}
      <CardContent>
        <Typography variant="h6" component="div" gutterBottom>
          {title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {description}
        </Typography>
      </CardContent>
    </Card>
  );
}

export default ManageItem;