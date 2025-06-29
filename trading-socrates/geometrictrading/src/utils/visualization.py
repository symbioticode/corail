import plotly.graph_objects as go
def plot_manifold(data, x='T', y='V', z='Phi'):
    fig = go.Figure(data=[go.Scatter3d(
        x=data[x], y=data[y], z=data[z],
        mode='markers', marker=dict(size=5, color=data['H'], colorscale='Viridis')
    )])
    fig.update_layout(title='Manifold QAAF 3D', scene=dict(xaxis_title=x, yaxis_title=y, zaxis_title=z))
    fig.show()
