import { Component } from 'react';
import { StateMessage } from '@/components/ui/StateMessage';

/**
 * Catches render-time exceptions. React unmounts the whole tree when a render
 * throws, so without a boundary a single broken component leaves a blank page.
 * Error boundaries have no hook equivalent, which is why this is a class.
 */
export class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error('Falha de renderização:', error, info?.componentStack);
  }

  handleReset = () => {
    this.setState({ error: null });
  };

  render() {
    if (!this.state.error) {
      return this.props.children;
    }

    return (
      <div className="container py-5">
        <StateMessage
          icon="warning"
          title="Algo quebrou nesta tela"
          description="O erro foi registrado. Tente novamente ou volte ao início."
          action={
            <div className="d-flex gap-2 justify-content-center">
              <button type="button" className="btn-climora btn-climora--primary btn-climora--pill" onClick={this.handleReset}>
                Tentar novamente
              </button>
              <a href="/" className="btn-climora btn-climora--secondary btn-climora--pill">
                Voltar ao início
              </a>
            </div>
          }
        />
      </div>
    );
  }
}
