import "./ActionButton.css";

function ActionButton(props) {
  return (
    <button
      className="action-button"
      style={{ backgroundColor: props.color }}
      onClick={props.onClick}
    >
      {props.text}
    </button>
  );
}

export default ActionButton;