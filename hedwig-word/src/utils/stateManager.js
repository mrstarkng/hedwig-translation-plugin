class StateManager {
  constructor(initialState, event) {
    this.state = initialState;

    const setStateInternal = (newState) => {
      this.state = newState;
    };

    this.setState = new Proxy(setStateInternal, {
      apply: (target, _, argumentList) => {
        target(...argumentList);
        dispatchEvent(event);
      },
    });
  }
}
export default StateManager;
