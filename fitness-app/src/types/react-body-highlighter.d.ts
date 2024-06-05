declare module 'react-body-highlighter' {
    import * as React from 'react';

    export interface IExerciseData {
        name: string;
        muscles: string[];
    }

    export interface IMuscleStats {
        muscle: string;
    }

    export interface IModelProps {
        data: IExerciseData[];
        style?: React.CSSProperties;
        onClick: (muscleStats: IMuscleStats) => void;
        highlightedColors?: string[];
    }

    export default class Model extends React.Component<IModelProps> { }
}
