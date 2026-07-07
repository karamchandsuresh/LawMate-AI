function ActionButton(props) {
  return (
    <button
      style={{ backgroundColor: props.color }}
    >
      {props.text}
    </button>
  );
}

export default ActionButton;